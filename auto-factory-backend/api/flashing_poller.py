"""刷机任务定时轮询模块

定时检查是否有 QUEUED / NO_DEVICE 状态的版本，
匹配空闲设备后自动下发刷机。
"""

import logging
import threading
import time
from django.db import connection

logger = logging.getLogger(__name__)

POLL_INTERVAL = 10  # 轮询间隔（秒）


def poll_flashing():
    """检查并触发待刷版本的刷机任务"""
    from .models import Version
    from .flashing_dispatcher import dispatch_flashing

    # 候选版本：QUEUED(1) 或 NO_DEVICE(0)
    candidates = Version.objects.filter(
        status__in=[Version.Status.QUEUED, Version.Status.NO_DEVICE]
    ).select_related('branch').order_by('-created_at')

    if not candidates.exists():
        return

    logger.debug('刷机轮询: 发现 %d 个候选版本', candidates.count())

    for version in candidates:
        result = dispatch_flashing(version.id)
        if result.get('success'):
            logger.info('刷机轮询: 版本 %s 刷机已下发 (%d 台设备)',
                       version.version, result.get('process_count', 0))
        elif result.get('no_device'):
            # 没有空闲设备，跳过，等下次轮询
            logger.debug('刷机轮询: 版本 %s 无空闲设备，跳过', version.version)
            continue
        else:
            logger.warning('刷机轮询: 版本 %s 下发失败: %s',
                          version.version, result.get('error'))


def _run_poller():
    """后台线程：循环轮询"""
    logger.info('刷机轮询线程已启动 (间隔 %ds)', POLL_INTERVAL)
    while True:
        try:
            connection.close()  # 关闭旧连接，防止泄漏
            poll_flashing()
        except Exception as e:
            logger.error('刷机轮询异常: %s', e, exc_info=True)
        time.sleep(POLL_INTERVAL)


def start_poller():
    """启动轮询后台线程（Django ready() 时调用）"""
    thread = threading.Thread(target=_run_poller, daemon=True, name='flashing-poller')
    thread.start()
    logger.info('刷机轮询后台线程已启动')
