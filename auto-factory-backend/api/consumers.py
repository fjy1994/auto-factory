"""
WebSocket 消费者
"""

import json
from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer

# 存储在线的Agent连接: executor_id -> consumer instance
ONLINE_AGENTS = {}


def send_command_to_agent(executor_id, command):
    """向指定Agent发送指令"""
    if executor_id in ONLINE_AGENTS:
        try:
            ONLINE_AGENTS[executor_id].send_json(command)
            return True
        except Exception:
            pass
    return False


class AgentConsumer(WebsocketConsumer):
    """Agent WebSocket连接"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.executor_id = None
    
    def connect(self):
        # 接受连接（等待注册消息）
        self.accept()
    
    def disconnect(self, close_code):
        # 移除连接
        if self.executor_id and self.executor_id in ONLINE_AGENTS:
            del ONLINE_AGENTS[self.executor_id]
            print(f'Agent断开连接: {self.executor_id}, 当前在线: {len(ONLINE_AGENTS)}')
        raise StopConsumer()
    
    def receive(self, text_data=None, bytes_data=None):
        try:
            message = json.loads(text_data)
            
            # 处理注册消息
            if message.get('type') == 'register':
                self.executor_id = message.get('executorId')
                ONLINE_AGENTS[self.executor_id] = self
                print(f'Agent已注册: {self.executor_id}, 当前在线: {len(ONLINE_AGENTS)}')
                return
            
            # 处理心跳
            if message.get('type') == 'ping':
                self.send_json({'type': 'pong'})
                return
            
            # 处理任务进度上报
            if message.get('type') == 'task_progress':
                print(f'收到任务进度: {message}')
                # TODO: 更新数据库中的任务进度
                return
            
        except json.JSONDecodeError:
            print(f'收到无效JSON: {text_data}')
    
    def send_json(self, data):
        """发送JSON消息"""
        self.send(text_data=json.dumps(data, ensure_ascii=False))
