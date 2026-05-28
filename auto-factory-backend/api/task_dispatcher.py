"""
任务调度器：将 Task 的用例分批下发到 Agent 执行

工作流程：
1. 从 Task.case_ids 获取所有用例 ID
2. 按 Task.batch_size 分成多个批次
3. 跳过已完成的批次，发送当前批次到 Agent
4. Agent 执行完后回调 report_batch 提交结果
5. 更新 Task 进度，继续下一批，直至完成
"""

import logging
import requests
import json
from django.db import connection

logger = logging.getLogger(__name__)


def get_cases_batch(task_id: int) -> list:
    """获取任务中等待执行的用例列表（含 script_path）"""
    from .models import Task, TestCase

    connection.close_if_unusable()
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        logger.error(f'任务 {task_id} 不存在')
        return []

    # 获取所有用例 ID
    all_case_ids = task.case_ids or []
    if not all_case_ids:
        logger.warning(f'任务 {task_id} 没有关联用例')
        return []

    # 计算当前批次的范围
    completed = len(task.case_results or [])
    batch_size = task.batch_size or 10
    batch_start = completed
    batch_end = min(batch_start + batch_size, len(all_case_ids))

    if batch_start >= len(all_case_ids):
        return []

    batch_case_ids = all_case_ids[batch_start:batch_end]

    # 查询用例详细信息（含脚本路径）
    cases_info = []
    for case_id in batch_case_ids:
        try:
            tc = TestCase.objects.get(case_id=case_id)
            cases_info.append({
                'case_id': tc.case_id,
                'script_path': tc.script_path or '',
                'name': tc.name,
            })
        except TestCase.DoesNotExist:
            logger.warning(f'用例 {case_id} 不存在，跳过')
            cases_info.append({
                'case_id': case_id,
                'script_path': '',
                'name': '',
            })

    return cases_info


def dispatch_task(task_id: int):
    """
    调度任务：获取下一批用例，发送到 Agent 执行
    这是同步 HTTP 调用，会阻塞直到 Agent 返回结果
    """
    from .models import Task

    connection.close_if_unusable()
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        logger.error(f'任务 {task_id} 不存在')
        return

    if task.status != 'running':
        logger.warning(f'任务 {task_id} 状态不是 running，跳过调度')
        return

    if not task.agent_url:
        logger.error(f'任务 {task_id} 没有配置 Agent 地址')
        task.status = 'failed'
        task.save(update_fields=['status'])
        return

    # 获取当前批次的用例
    batch_cases = get_cases_batch(task_id)
    if not batch_cases:
        # 没有更多用例，已完成
        from django.utils import timezone
        task.status = 'success'
        task.progress = 100
        task.end_time = timezone.now()
        task.save(update_fields=['status', 'progress', 'end_time'])
        logger.info(f'任务 {task_id} 所有批次已完成')
        return

    batch_index = task.current_batch

    # 构造 Agent 请求
    agent_url = task.agent_url.rstrip('/')
    payload = {
        'task_id': task_id,
        'batch_index': batch_index,
        'cases': batch_cases,
        'params': {},
    }

    logger.info(f'任务 {task_id} 发送第 {batch_index} 批（{len(batch_cases)} 个用例）到 {agent_url}')

    try:
        resp = requests.post(
            f'{agent_url}/execute_batch',
            json=payload,
            timeout=3600,  # Agent 执行超时 1 小时
        )
        resp.raise_for_status()
        result_data = resp.json()

        # 将结果提交到 report_batch 端点
        from django.test import RequestFactory
        from .views import TaskViewSet
        from rest_framework.test import APIRequestFactory
        # 直接调用 report_batch 逻辑
        _handle_batch_results(task_id, batch_index, result_data.get('results', []))

    except requests.exceptions.Timeout:
        logger.error(f'任务 {task_id} 第 {batch_index} 批请求超时')
        task = Task.objects.get(id=task_id)
        task.status = 'failed'
        task.log = (task.log or '') + f'\n批次 {batch_index} 请求 Agent 超时'
        task.save(update_fields=['status', 'log'])

    except requests.exceptions.ConnectionError as e:
        logger.error(f'任务 {task_id} 连接 Agent 失败: {e}')
        task = Task.objects.get(id=task_id)
        task.status = 'failed'
        task.log = (task.log or '') + f'\n连接 Agent 失败: {e}'
        task.save(update_fields=['status', 'log'])

    except requests.exceptions.RequestException as e:
        logger.error(f'任务 {task_id} 请求 Agent 出错: {e}')
        task = Task.objects.get(id=task_id)
        task.status = 'failed'
        task.log = (task.log or '') + f'\n请求 Agent 出错: {e}'
        task.save(update_fields=['status', 'log'])


def _handle_batch_results(task_id: int, batch_index: int, results: list):
    """处理批次结果"""
    from .models import Task
    from django.utils import timezone

    connection.close_if_unusable()
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        logger.error(f'任务 {task_id} 不存在')
        return

    # 检查批次序号
    if batch_index != task.current_batch:
        logger.warning(f'批次序号不匹配: 期望 {task.current_batch}，收到 {batch_index}')
        return

    # 追加结果
    task.case_results = (task.case_results or []) + results
    task.current_batch += 1

    # 更新统计数据
    pass_count = sum(1 for r in task.case_results if r.get('status') == 'passed')
    fail_count = sum(1 for r in task.case_results if r.get('status') in ('failed', 'error'))
    task.pass_count = pass_count
    task.fail_count = fail_count
    task.progress = int(len(task.case_results) / task.total_count * 100) if task.total_count > 0 else 0
    task.pass_rate = round(pass_count / len(task.case_results) * 100, 1) if task.case_results else 0

    # 判断是否所有批次完成
    if task.current_batch * task.batch_size >= task.total_count:
        task.status = 'success'
        task.progress = 100
        task.end_time = timezone.now()

    task.save(update_fields=[
        'case_results', 'current_batch', 'pass_count', 'fail_count',
        'progress', 'pass_rate', 'status', 'end_time',
    ])

    logger.info(f'任务 {task_id} 第 {batch_index} 批完成，进度 {task.progress}%')

    # 如果还有下一批，继续调度
    if task.status == 'running':
        dispatch_task(task_id)
