"""
任务调度器：将 Task 的用例分批下发到 Agent 执行

数据来源：
  - 用例列表来自 TaskDef.case_ids ∪ TaskDef.case_set_ids → TestCase
  - 批次大小来自 TaskDef.batch_size
  - 结果写入 TaskResult 表

流程：
  1. 汇总 TaskDef 的关联用例（case_ids + case_set_ids 展开去重）
  2. 按 batch_size 分组，跳过已完成的批次
  3. 发送当前批次到 Agent 执行
  4. Agent 回调提交结果
  5. 更新 Task 进度，继续下一批
"""

import logging
import requests
from django.db import connection
from django.utils import timezone

logger = logging.getLogger(__name__)


def _collect_case_ids(task_def):
    """汇总任务定义中的所有用例 ID（case_ids + case_set_ids 展开去重）"""
    from .models import CaseSet

    case_ids = set(task_def.case_ids or [])
    for cs_id in (task_def.case_set_ids or []):
        try:
            cs = CaseSet.objects.get(id=cs_id)
            case_ids.update(cs.case_ids or [])
        except CaseSet.DoesNotExist:
            logger.warning(f'用例集 {cs_id} 不存在，跳过')
    return sorted(case_ids)


def get_cases_batch(task_id: int) -> list:
    """获取任务中等待执行的用例列表（含 script_path）"""
    from .models import Task, TestCase, TaskDef

    connection.close_if_unusable()
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        logger.error(f'任务 {task_id} 不存在')
        return []

    if not task.task_def:
        logger.warning(f'任务 {task_id} 没有关联任务定义')
        return []

    task_def = task.task_def
    all_case_ids = _collect_case_ids(task_def)
    if not all_case_ids:
        logger.warning(f'任务 {task_id} 没有关联用例')
        return []

    # 已完成数
    completed = TaskResult.objects.filter(task=task).count()
    batch_size = task_def.batch_size or 10
    batch_start = completed
    batch_end = min(batch_start + batch_size, len(all_case_ids))

    if batch_start >= len(all_case_ids):
        return []

    batch_case_ids = all_case_ids[batch_start:batch_end]

    # 查询用例详细信息
    cases_info = []
    for cid in batch_case_ids:
        try:
            tc = TestCase.objects.get(case_id=str(cid))
            cases_info.append({
                'case_id': tc.case_id,
                'script_path': tc.script_path or '',
                'name': tc.name,
            })
        except TestCase.DoesNotExist:
            logger.warning(f'用例 {cid} 不存在，跳过')
            cases_info.append({
                'case_id': str(cid),
                'script_path': '',
                'name': '',
            })

    return cases_info


def dispatch_task(task_id: int):
    """
    调度任务：获取下一批用例，发送到 Agent 执行
    （需配合外部 Agent 地址配置使用）
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

    # 获取当前批次的用例
    batch_cases = get_cases_batch(task_id)
    if not batch_cases:
        # 没有更多用例，已完成
        task.status = 'completed'
        task.progress = 100
        task.end_time = timezone.now()
        task.save(update_fields=['status', 'progress', 'end_time'])
        logger.info(f'任务 {task_id} 所有批次已完成')
        return

    # Agent 地址需外部配置，这里以 task 的额外记录方式存储
    # 实际项目中可以从外部系统或配置读取
    logger.info(f'任务 {task_id} 获取到 {len(batch_cases)} 个待执行用例，等待 Agent 拉取')


def _handle_batch_results(task_id: int, results: list):
    """处理 Agent 回调返回的批次结果"""
    from .models import Task, TaskResult, TestCase
    from django.utils import timezone

    connection.close_if_unusable()
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        logger.error(f'任务 {task_id} 不存在')
        return

    now = timezone.now()
    for r in results:
        case_id = r.get('case_id', '')
        TaskResult.objects.create(
            task=task,
            case_id=case_id,
            status=r.get('status', 'failed'),
            error_message=r.get('error_message', ''),
            duration=r.get('duration'),
            start_time=r.get('start_time', now),
            end_time=r.get('end_time', now),
        )

    # 更新统计数据
    all_results = TaskResult.objects.filter(task=task)
    total = all_results.count()
    passed = all_results.filter(status='passed').count()
    failed = all_results.filter(status='failed').count()

    task.pass_count = passed
    task.fail_count = failed
    task.total_count = total
    task.progress = min(100, int(total / max(task.total_count or 1, 1) * 100))
    task.pass_rate = round(passed / total * 100, 1) if total > 0 else 0

    # 判断是否完成
    total_expected = _collect_case_ids(task.task_def) if task.task_def else []
    if total >= len(total_expected):
        task.status = 'completed'
        task.progress = 100
        task.end_time = now

    task.save(update_fields=[
        'pass_count', 'fail_count', 'total_count',
        'progress', 'pass_rate', 'status', 'end_time',
    ])

    logger.info(f'任务 {task_id} 进度 {task.progress}%：{passed}通过/{failed}失败')

    # 如果还有下一批，继续调度
    if task.status == 'running':
        dispatch_task(task_id)
