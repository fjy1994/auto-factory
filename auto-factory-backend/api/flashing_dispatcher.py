"""刷机任务调度模块

负责：
- 自动匹配设备并创建刷机过程
- 向 Agent 发送刷机指令
- 处理 Agent 回调结果
- 刷机完成后自动更新 Version 状态
"""

import logging
import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import Version, FlashingTask, FlashingProcess, Device, TaskDef

logger = logging.getLogger(__name__)

# 刷机步骤定义（顺序敏感）
STEP_NAMES = ['env_check', 'download_rom', 'flash', 'setup_wizard', 'connect_wifi']


def _get_agent_base(device):
    """获取 Agent 基础 URL"""
    executor_ip = device.executor_ip or '127.0.0.1'
    port = getattr(settings, 'AGENT_DEFAULT_PORT', 18000)
    return f'http://{executor_ip}:{port}'


@transaction.atomic
def dispatch_flashing(version_id):
    """为指定版本下发刷机任务

    1. 获取 Version 和关联的分支 TaskDef 设备约束
    2. 按 device_quantity / device_models 匹配空闲设备
    3. 创建 FlashingProcess 记录
    4. 逐一通知 Agent 开始刷机

    Returns: dict
    """
    try:
        version = Version.objects.select_related('branch').get(id=version_id)
    except Version.DoesNotExist:
        return {'success': False, 'error': '版本不存在'}

    # 仅 NO_DEVICE / QUEUED 状态允许下发
    if version.status not in (0, 1):
        return {
            'success': False,
            'error': f'版本状态 {version.get_status_display()} 不允许下发刷机',
        }

    branch = version.branch
    # 收集分支所有 TaskDef 的设备约束
    task_defs = TaskDef.objects.filter(branch=branch)

    allowed_models = set()
    max_devices = 0  # 0 = 不限制
    for td in task_defs:
        models = td.device_models or []
        if models:
            allowed_models.update(models)
        if td.device_quantity and td.device_quantity > 0:
            max_devices = max(max_devices, td.device_quantity)

    # 查找空闲设备
    devices = Device.objects.filter(status='idle')
    if allowed_models:
        devices = devices.filter(model__in=list(allowed_models))
    if max_devices > 0:
        devices = devices[:max_devices]

    if not devices.exists():
        logger.info('版本 %s 下发刷机: 无可用空闲设备', version.version)
        version.status = 0  # NO_DEVICE
        version.save(update_fields=['status'])
        return {'success': False, 'error': '没有可用的空闲设备', 'no_device': True}

    # 更新版本状态为 FLASHING(2)
    version.status = 2
    version.save(update_fields=['status'])

    # 创建/获取 FlashingTask
    flashing_task, _ = FlashingTask.objects.get_or_create(version=version)
    flashing_task.status = 'running'
    flashing_task.save(update_fields=['status'])

    # 为每个设备创建 FlashingProcess
    created_processes = []
    for device in devices:
        steps = [{'name': name, 'status': 'pending'} for name in STEP_NAMES]
        process = FlashingProcess.objects.create(
            flashing_task=flashing_task,
            device=device,
            steps=steps,
            status='pending',
        )
        # 设备标记为刷机中
        Device.objects.filter(id=device.id).update(status='flashing')
        created_processes.append(process)

    # 逐一通知 Agent
    results = []
    for process in created_processes:
        result = _notify_agent(process)
        results.append({
            'process_id': process.id,
            'device_serial': process.device.serial,
            'notify_ok': result.get('ok', False),
            'error': result.get('error'),
        })

    return {
        'success': True,
        'version_id': version.id,
        'version_label': version.version,
        'process_count': len(created_processes),
        'processes': results,
    }


def _notify_agent(process):
    """向 Agent 发送刷机指令

    Agent 接口:
    POST /agent/flash/start
    { process_id, device_serial, device_model, rom_url, branch_name, version_label, steps }
    """
    device = process.device
    agent_base = _get_agent_base(device)
    version = process.flashing_task.version

    # 构建 ROM 下载地址（如已配置）
    rom_url = getattr(settings, 'ROM_DOWNLOAD_BASE_URL', '').rstrip('/')
    if rom_url and version.version:
        rom_url = f'{rom_url}/{version.version}.zip'

    payload = {
        'process_id': process.id,
        'device_serial': device.serial,
        'device_model': device.model or '',
        'rom_url': rom_url,
        'branch_name': version.branch.name if version.branch else '',
        'version_label': version.version,
        'steps': STEP_NAMES,
    }

    url = f'{agent_base}/agent/flash/start'
    timeout = getattr(settings, 'AGENT_REQUEST_TIMEOUT', 10)

    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        if resp.status_code < 500:
            # Agent 已接收，将第一步标记为 running
            _set_step_status(process.id, 'env_check', 'running')
            return {'ok': True, 'response': resp.json() if resp.content else {}}
        else:
            return {'ok': False, 'error': f'Agent 返回 {resp.status_code}'}
    except requests.ConnectionError:
        logger.warning('Agent 不可达: %s', url)
        return {'ok': False, 'error': f'Agent 连接失败 ({agent_base})'}
    except requests.Timeout:
        return {'ok': False, 'error': 'Agent 请求超时'}
    except Exception as e:
        logger.exception('通知 Agent 异常')
        return {'ok': False, 'error': str(e)}


@transaction.atomic
def handle_step_callback(process_id, step_name, status, error_message=''):
    """处理 Agent 回调的步骤执行结果

    Args:
        process_id: FlashingProcess ID
        step_name: 步骤名
        status: 'success' 或 'failed'
        error_message: 错误描述

    Returns: dict
    """
    try:
        process = FlashingProcess.objects.select_related(
            'flashing_task__version', 'device'
        ).get(id=process_id)
    except FlashingProcess.DoesNotExist:
        return {'success': False, 'error': '刷机过程不存在'}

    if status not in ('success', 'failed'):
        return {'success': False, 'error': f'无效状态: {status}'}
    if step_name not in STEP_NAMES:
        return {'success': False, 'error': f'无效步骤名: {step_name}'}

    steps = list(process.steps or [])
    updated = False
    next_step = None
    for i, step in enumerate(steps):
        if step['name'] == step_name:
            step['status'] = status
            if status == 'failed':
                step['errorMessage'] = error_message or '步骤失败'
            updated = True
            # 找下一个 pending 步骤
            for j in range(i + 1, len(steps)):
                if steps[j]['status'] == 'pending':
                    next_step = steps[j]['name']
                    break
            break

    if not updated:
        return {'success': False, 'error': f'步骤 {step_name} 未找到'}

    process.steps = steps

    if status == 'failed':
        process.status = 'failed'
        process.error_message = error_message or f'步骤 {step_name} 失败'
        process.save(update_fields=['steps', 'status', 'error_message', 'updated_at'])
        _set_device_idle(process.device_id)
        _check_version_completion(process.flashing_task.version)
        return {'success': True, 'process_status': 'failed'}

    if next_step:
        # 标记下一步为 running
        for step in steps:
            if step['name'] == next_step:
                step['status'] = 'running'
                break
        process.steps = steps
        process.status = 'running'
        process.save(update_fields=['steps', 'status', 'updated_at'])
        # 通知 Agent 执行下一步
        _notify_agent_step(process, next_step)
        return {'success': True, 'process_status': 'running', 'next_step': next_step}

    # 所有步骤完成
    # 检查是否有步骤在 running（说明有并发执行未完成）
    has_running = any(s['status'] == 'running' for s in steps)
    if has_running:
        process.status = 'running'
        process.save(update_fields=['steps', 'status', 'updated_at'])
        return {'success': True, 'process_status': 'running'}

    process.status = 'success'
    process.save(update_fields=['steps', 'status', 'updated_at'])
    _set_device_idle(process.device_id)
    _check_version_completion(process.flashing_task.version)
    return {'success': True, 'process_status': 'success', 'next_step': None}


def _notify_agent_step(process, step_name):
    """通知 Agent 执行指定步骤"""
    device = process.device
    agent_base = _get_agent_base(device)
    payload = {
        'process_id': process.id,
        'device_serial': device.serial,
        'step': step_name,
    }
    url = f'{agent_base}/agent/flash/step'
    timeout = getattr(settings, 'AGENT_REQUEST_TIMEOUT', 10)
    try:
        requests.post(url, json=payload, timeout=timeout)
    except Exception as e:
        logger.warning('通知 Agent 执行步骤 %s 失败: %s', step_name, e)


@transaction.atomic
def retry_process_step(process_id, step_name):
    """重置指定步骤（重试），并通知 Agent"""
    try:
        process = FlashingProcess.objects.select_related(
            'flashing_task__version', 'device'
        ).get(id=process_id)
    except FlashingProcess.DoesNotExist:
        return {'success': False, 'error': '刷机过程不存在'}

    steps = list(process.steps or [])
    found = False
    for step in steps:
        if step['name'] == step_name:
            step['status'] = 'running'
            step['retry_count'] = (step.get('retry_count') or 0) + 1
            step['errorMessage'] = ''
            found = True
            break

    if not found:
        return {'success': False, 'error': f'步骤 {step_name} 未找到'}

    # 将该步骤之后的所有步骤重置为 pending
    step_index = None
    for i, s in enumerate(steps):
        if s['name'] == step_name:
            step_index = i
            break
    if step_index is not None:
        for i in range(step_index + 1, len(steps)):
            steps[i]['status'] = 'pending'
            steps[i]['retry_count'] = 0
            steps[i]['errorMessage'] = ''

    process.steps = steps
    process.status = 'running'
    process.error_message = ''
    process.save(update_fields=['steps', 'status', 'error_message', 'updated_at'])

    # 通知 Agent
    _notify_agent_step(process, step_name)

    return {'success': True}


@transaction.atomic
def retry_process_all(process_id):
    """从头重新开始整个刷机流程"""
    try:
        process = FlashingProcess.objects.select_related(
            'flashing_task__version', 'device'
        ).get(id=process_id)
    except FlashingProcess.DoesNotExist:
        return {'success': False, 'error': '刷机过程不存在'}

    steps = [{'name': name, 'status': 'pending'} for name in STEP_NAMES]
    # 第一步标记为 running 并通知
    steps[0]['status'] = 'running'

    process.steps = steps
    process.status = 'running'
    process.retry_count = (process.retry_count or 0) + 1
    process.error_message = ''
    process.save(update_fields=['steps', 'status', 'retry_count', 'error_message', 'updated_at'])

    _notify_agent_step(process, 'env_check')

    return {'success': True}


# ─────────────── 内部辅助 ───────────────


def _set_step_status(process_id, step_name, status):
    """快速更新步骤状态"""
    try:
        process = FlashingProcess.objects.get(id=process_id)
        steps = list(process.steps or [])
        for step in steps:
            if step['name'] == step_name:
                step['status'] = status
                break
        process.steps = steps
        process.save(update_fields=['steps', 'updated_at'])
    except FlashingProcess.DoesNotExist:
        pass


def _set_device_idle(device_id):
    """恢复设备为空闲状态"""
    try:
        Device.objects.filter(id=device_id).update(status='idle')
    except Exception:
        pass


def _check_version_completion(version):
    """检查版本下所有刷机过程是否结束，更新 Version 状态

    决策逻辑（来自设计文档）：
    - 全部完成且至少一台成功 → TESTING(4)
    - 全部失败 → FLASH_FAILED(3)
    - 仍有机在刷 → 不动
    """
    processes = FlashingProcess.objects.filter(flashing_task__version=version)
    total = processes.count()
    if total == 0:
        return

    success_count = processes.filter(status='success').count()
    failed_count = processes.filter(status='failed').count()
    running_count = processes.filter(status__in=['pending', 'running']).count()

    if running_count > 0:
        return  # 还有设备在处理中

    if success_count == 0 and failed_count == total:
        version.status = 3  # FLASH_FAILED
    elif success_count > 0:
        version.status = 4  # TESTING
    # 其他情况不动

    version.save(update_fields=['status'])

    # 同步更新 FlashingTask 状态
    try:
        flashing_task = version.flashing_task
        if flashing_task.status != 'success' and success_count > 0 and running_count == 0:
            flashing_task.status = 'success'
        elif flashing_task.status != 'failed' and success_count == 0 and failed_count == total:
            flashing_task.status = 'failed'
        flashing_task.save(update_fields=['status'])
    except FlashingTask.DoesNotExist:
        pass
