#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化工厂设备代理Agent
功能：定时扫描本地设备信息并上报给主服务
"""

import os
import re
import json
import time
import socket
import logging
import subprocess
import threading
from datetime import datetime
from typing import List, Dict, Optional

import requests
import schedule
import websocket

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('device_agent.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DeviceAgent:
    def __init__(self):
        """初始化Agent（无配置文件版本）"""
        # 所有配置都写死在代码里
        self.server_url = 'http://localhost:8000'
        self.ws_url = 'ws://localhost:8000/ws/agent'
        self.adb_path = 'adb'
        self.report_interval = 60
        
        # 执行机ID直接用本地IP
        self.executor_ip = self._get_local_ip()
        self.executor_id = self.executor_ip
        
        self.ws = None
        self.ws_thread = None
        self.running = False
        
        logger.info(f"设备Agent初始化完成")
        logger.info(f"执行机IP: {self.executor_ip}")
        logger.info(f"执行机ID: {self.executor_id}")
        logger.info(f"主服务地址: {self.server_url}")
        logger.info(f"上报间隔: {self.report_interval}秒")

    def _get_local_ip(self) -> str:
        """获取本机IP地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return 'unknown'

    def _run_adb_command(self, command: str, serial: Optional[str] = None) -> str:
        """执行ADB命令"""
        try:
            if serial:
                cmd = f'"{self.adb_path}" -s {serial} {command}'
            else:
                cmd = f'"{self.adb_path}" {command}'
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=30
            )
            return result.stdout.strip() if result.returncode == 0 else ''
        except Exception as e:
            logger.debug(f"执行ADB命令失败: {e}")
            return ''

    def get_connected_devices(self) -> List[str]:
        """获取已连接的设备序列号列表"""
        output = self._run_adb_command('devices')
        serials = []
        for line in output.split('\n'):
            line = line.strip()
            if line and '\t' in line and line != 'List of devices attached':
                parts = line.split('\t')
                if len(parts) >= 2 and parts[1] == 'device':
                    serials.append(parts[0])
        return serials

    def get_device_rom_version(self, serial: str) -> str:
        """获取设备ROM版本"""
        # 尝试多种方式获取ROM版本
        commands = [
            'shell getprop ro.build.display.id',
            'shell getprop ro.build.version.release',
            'shell getprop ro.product.model'
        ]
        for cmd in commands:
            result = self._run_adb_command(cmd, serial)
            if result:
                return result
        return '未知'

    def get_device_browser_version(self, serial: str) -> str:
        """获取浏览器版本"""
        # 尝试获取Chrome版本
        result = self._run_adb_command('shell dumpsys package com.android.chrome', serial)
        if result:
            match = re.search(r'versionName=([\d.]+)', result)
            if match:
                return f'Chrome {match.group(1)}'
        
        # 尝试获取系统浏览器版本
        result = self._run_adb_command('shell dumpsys package com.android.browser', serial)
        if result:
            match = re.search(r'versionName=([\d.]+)', result)
            if match:
                return f'Browser {match.group(1)}'
        
        return '未知'

    def get_device_info(self, serial: str) -> Dict:
        """获取单个设备的详细信息"""
        return {
            'serial': serial,
            'romVersion': self.get_device_rom_version(serial),
            'browserVersion': self.get_device_browser_version(serial),
            'executorIp': self.executor_ip,
            'status': 'idle',  # 初始状态为空闲，主服务会根据任务状态更新
            'lastReportTime': datetime.now().isoformat(),
            'remark': ''
        }

    def scan_devices(self) -> List[Dict]:
        """扫描所有本地设备"""
        logger.info("开始扫描设备...")
        serials = self.get_connected_devices()
        devices = []
        
        for serial in serials:
            try:
                device_info = self.get_device_info(serial)
                devices.append(device_info)
                logger.info(f"发现设备: {serial} - {device_info['romVersion']}")
            except Exception as e:
                logger.error(f"获取设备 {serial} 信息失败: {e}")
        
        logger.info(f"扫描完成，共发现 {len(devices)} 台设备")
        return devices

    def report_devices(self, devices: List[Dict]) -> bool:
        """上报设备信息到主服务"""
        try:
            payload = {
                'executorId': self.config.get('executor_id', self.executor_ip),
                'executorIp': self.executor_ip,
                'reportTime': datetime.now().isoformat(),
                'devices': devices
            }
            
            url = f"{self.server_url}/api/v1/agent/report"
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"设备信息上报成功，共 {len(devices)} 台设备")
                return True
            else:
                logger.error(f"设备信息上报失败，状态码: {response.status_code}, 响应: {response.text}")
                return False
        except Exception as e:
            logger.error(f"上报设备信息异常: {e}")
            return False

    def scan_and_report(self):
        """扫描并上报设备（定时任务入口）"""
        devices = self.scan_devices()
        self.report_devices(devices)

    # ==================== WebSocket相关方法 ====================
    
    def on_message(self, ws, message):
        """收到WebSocket消息"""
        try:
            logger.info(f"收到指令: {message}")
            data = json.loads(message)
            command = data.get('command')
            device_serial = data.get('deviceSerial')
            task_id = data.get('taskId')
            
            if command == 'reboot':
                self._handle_reboot(device_serial, task_id)
            elif command == 'flash_rom':
                self._handle_flash_rom(device_serial, data.get('romVersion'), task_id)
            elif command == 'ping':
                self._send_ws_message({'type': 'pong'})
            else:
                logger.warning(f"未知指令: {command}")
        except Exception as e:
            logger.error(f"处理WebSocket消息失败: {e}")

    def on_error(self, ws, error):
        """WebSocket错误"""
        logger.error(f"WebSocket错误: {error}")

    def on_open(self, ws):
        """WebSocket连接建立"""
        logger.info("WebSocket连接已建立")
        # 发送注册信息
        self._send_ws_message({
            'type': 'register',
            'executorId': self.config.get('executor_id', self.executor_ip),
            'executorIp': self.executor_ip
        })

    def on_close(self, ws, close_status_code, close_msg):
        """WebSocket连接关闭"""
        logger.info(f"WebSocket连接已关闭: {close_status_code} - {close_msg}")

    def _send_ws_message(self, message: Dict):
        """发送WebSocket消息"""
        if self.ws and self.ws.sock and self.ws.sock.connected:
            try:
                self.ws.send(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                logger.error(f"发送WebSocket消息失败: {e}")

    def _handle_reboot(self, device_serial: str, task_id: Optional[int] = None):
        """处理重启设备指令"""
        logger.info(f"执行重启设备指令: {device_serial}")
        try:
            # 上报开始执行
            self._send_ws_message({
                'type': 'task_progress',
                'taskId': task_id,
                'deviceSerial': device_serial,
                'status': 'running',
                'progress': 10,
                'message': '开始重启设备...'
            })
            
            # 执行重启命令
            result = self._run_adb_command('reboot', device_serial)
            
            # 上报完成
            self._send_ws_message({
                'type': 'task_progress',
                'taskId': task_id,
                'deviceSerial': device_serial,
                'status': 'success',
                'progress': 100,
                'message': '设备重启指令已发送'
            })
            
            logger.info(f"设备 {device_serial} 重启指令已发送")
        except Exception as e:
            logger.error(f"重启设备失败: {e}")
            self._send_ws_message({
                'type': 'task_progress',
                'taskId': task_id,
                'deviceSerial': device_serial,
                'status': 'failed',
                'progress': 0,
                'message': f'重启失败: {str(e)}'
            })

    def _handle_flash_rom(self, device_serial: str, rom_version: str, task_id: Optional[int] = None):
        """处理刷机指令"""
        logger.info(f"执行刷机指令: {device_serial}, ROM版本: {rom_version}")
        try:
            # 上报开始执行
            self._send_ws_message({
                'type': 'task_progress',
                'taskId': task_id,
                'deviceSerial': device_serial,
                'status': 'running',
                'progress': 10,
                'message': '开始刷机流程...'
            })
            
            # 这里可以调用实际的刷机脚本
            # TODO: 实现实际的刷机逻辑
            # subprocess.run(['flash_script.bat', device_serial, rom_version])
            
            # 模拟刷机进度上报
            for progress in [30, 50, 70, 90]:
                self._send_ws_message({
                    'type': 'task_progress',
                    'taskId': task_id,
                    'deviceSerial': device_serial,
                    'status': 'running',
                    'progress': progress,
                    'message': f'刷机中... {progress}%'
                })
                time.sleep(2)
            
            # 上报完成
            self._send_ws_message({
                'type': 'task_progress',
                'taskId': task_id,
                'deviceSerial': device_serial,
                'status': 'success',
                'progress': 100,
                'message': '刷机完成'
            })
            
            logger.info(f"设备 {device_serial} 刷机完成")
        except Exception as e:
            logger.error(f"刷机失败: {e}")
            self._send_ws_message({
                'type': 'task_progress',
                'taskId': task_id,
                'deviceSerial': device_serial,
                'status': 'failed',
                'progress': 0,
                'message': f'刷机失败: {str(e)}'
            })

    def start_websocket(self):
        """启动WebSocket连接"""
        if not self.config.get('ws_url'):
            logger.warning("未配置WebSocket地址，跳过WebSocket连接")
            return
        
        try:
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            
            self.ws_thread = threading.Thread(target=self.ws.run_forever, daemon=True)
            self.ws_thread.start()
            logger.info("WebSocket连接线程已启动")
        except Exception as e:
            logger.error(f"启动WebSocket失败: {e}")

    # ==================== 启动方法 ====================
    
    def start(self):
        """启动Agent"""
        logger.info("=" * 50)
        logger.info("设备Agent启动中...")
        logger.info("=" * 50)
        
        self.running = True
        
        # 启动WebSocket
        self.start_websocket()
        
        # 立即执行一次扫描上报
        self.scan_and_report()
        
        # 设置定时任务
        schedule.every(self.report_interval).seconds.do(self.scan_and_report)
        
        logger.info(f"定时任务已启动，每 {self.report_interval} 秒上报一次")
        logger.info("按 Ctrl+C 停止Agent")
        
        # 运行主循环
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("收到停止信号，正在关闭...")
        finally:
            self.stop()

    def stop(self):
        """停止Agent"""
        self.running = False
        if self.ws:
            self.ws.close()
        logger.info("设备Agent已停止")


def main():
    """主函数"""
    agent = DeviceAgent()
    agent.start()


if __name__ == '__main__':
    main()
