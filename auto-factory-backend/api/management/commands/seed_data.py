"""
初始化种子数据
"""
from django.core.management.base import BaseCommand
from api.models import Device, Branch, Task, TestCase, CaseSet, TaskConfig, Executor, FlashingProcess, RomRecord
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = '初始化种子数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化种子数据...')

        # 清理旧数据
        RomRecord.objects.all().delete()
        FlashingProcess.objects.all().delete()
        TaskConfig.objects.all().delete()
        CaseSet.objects.all().delete()
        TestCase.objects.all().delete()
        Task.objects.all().delete()
        Executor.objects.all().delete()
        Device.objects.all().delete()
        Branch.objects.all().delete()

        # 设备
        devices_data = [
            {'serial': 'SN001', 'device_name': '小米14-01', 'model': '小米14', 'rom_version': 'V14.0.1', 'status': 'idle', 'executor_ip': '192.168.1.101'},
            {'serial': 'SN002', 'device_name': '小米14-02', 'model': '小米14', 'rom_version': 'V14.0.1', 'status': 'busy', 'executor_ip': '192.168.1.102'},
            {'serial': 'SN003', 'device_name': 'Redmi K70-01', 'model': 'Redmi K70', 'rom_version': 'V15.0.2', 'status': 'idle', 'executor_ip': '192.168.1.103'},
            {'serial': 'SN004', 'device_name': '小米13-01', 'model': '小米13', 'rom_version': 'V14.0.5', 'status': 'offline', 'executor_ip': ''},
            {'serial': 'SN005', 'device_name': '小米13-02', 'model': '小米13', 'rom_version': 'V14.0.5', 'status': 'idle', 'executor_ip': '192.168.1.105'},
        ]
        for d in devices_data:
            Device.objects.create(**d)
        self.stdout.write(f'  + 创建 {len(devices_data)} 个设备')

        # 分支
        branches_data = [
            {'name': 'DEV-V14.0.1', 'type': 'DEV', 'version': 'V14.0.1', 'model': '小米14', 'version_pattern': 'V14.0.*', 'mail_title_pattern': '[DEV] V14.0.*'},
            {'name': '主干-V15.0', 'type': '主干', 'version': 'V15.0.0', 'model': 'Redmi K70', 'version_pattern': 'V15.0.*', 'mail_title_pattern': '[主干] V15.0.*'},
            {'name': '商分-V14.0.5', 'type': '商分', 'version': 'V14.0.5', 'model': '小米13', 'version_pattern': 'V14.0.*', 'mail_title_pattern': '[商分] V14.0.*'},
        ]
        branches = []
        for b in branches_data:
            branches.append(Branch.objects.create(**b))
        self.stdout.write(f'  + 创建 {len(branches_data)} 个分支')

        # 任务
        tasks_data = [
            {'name': '小米14 V14.0.1 稳定性压力测试', 'branch': branches[0], 'branch_name': 'DEV-V14.0.1', 'version': 'V14.0.1', 'model': '小米14', 'task_type': '稳定性', 'status': 'running', 'progress': 65, 'device_serial': 'SN001', 'total_count': 100, 'pass_count': 60, 'fail_count': 5, 'start_time': datetime.now() - timedelta(hours=2)},
            {'name': 'Redmi K70 V15.0 功能回归', 'branch': branches[1], 'branch_name': '主干-V15.0', 'version': 'V15.0.0', 'model': 'Redmi K70', 'task_type': '功能回归', 'status': 'completed', 'progress': 100, 'device_serial': 'SN003', 'pass_rate': 95.0, 'total_count': 200, 'pass_count': 190, 'fail_count': 10, 'start_time': datetime.now() - timedelta(hours=5), 'end_time': datetime.now() - timedelta(hours=3)},
            {'name': '小米13 V14.0.5 兼容性测试', 'branch': branches[2], 'branch_name': '商分-V14.0.5', 'version': 'V14.0.5', 'model': '小米13', 'task_type': '兼容性', 'status': 'queued', 'progress': 0, 'device_serial': 'SN005', 'total_count': 150},
            {'name': '小米14 V14.0.1 性能测试', 'branch': branches[0], 'branch_name': 'DEV-V14.0.1', 'version': 'V14.0.1', 'model': '小米14', 'task_type': '性能', 'status': 'failed', 'progress': 30, 'device_serial': 'SN002', 'total_count': 80, 'pass_count': 20, 'fail_count': 4, 'start_time': datetime.now() - timedelta(hours=1)},
            {'name': 'Redmi K70 V15.0 压力测试', 'branch': branches[1], 'branch_name': '主干-V15.0', 'version': 'V15.0.0', 'model': 'Redmi K70', 'task_type': '压力', 'status': 'pending', 'progress': 0, 'device_serial': 'SN003', 'total_count': 500},
        ]
        for t in tasks_data:
            Task.objects.create(**t)
        self.stdout.write(f'  + 创建 {len(tasks_data)} 个任务')

        # 测试用例
        cases_data = [
            {'case_id': 'TC-001', 'name': '用户登录功能验证', 'module': '登录模块', 'priority': 'L0', 'steps': '1. 打开应用\n2. 输入用户名密码\n3. 点击登录', 'expected': '成功登录进入主页', 'creator': '张三'},
            {'case_id': 'TC-002', 'name': '用户注册功能验证', 'module': '登录模块', 'priority': 'L0', 'steps': '1. 打开注册页面\n2. 填写必填项\n3. 提交注册', 'expected': '注册成功并自动登录', 'creator': '张三'},
            {'case_id': 'TC-003', 'name': '首页加载性能', 'module': '性能测试', 'priority': 'L2', 'steps': '1. 打开应用\n2. 记录首页加载时间', 'expected': '首页在3秒内加载完成', 'creator': '李四'},
            {'case_id': 'TC-004', 'name': '搜索功能测试', 'module': '搜索', 'priority': 'L0', 'steps': '1. 进入搜索页面\n2. 输入关键词\n3. 查看搜索结果', 'expected': '搜索结果准确相关', 'creator': '李四'},
            {'case_id': 'TC-005', 'name': '主题切换功能', 'module': 'UI', 'priority': 'L4', 'steps': '1. 进入设置\n2. 切换主题\n3. 验证UI显示', 'expected': '主题切换成功，UI显示正常', 'creator': '王五'},
            {'case_id': 'TC-006', 'name': '消息推送验证', 'module': '消息', 'priority': 'L2', 'steps': '1. 触发推送事件\n2. 检查通知栏', 'expected': '收到正确推送消息', 'creator': '王五'},
            {'case_id': 'TC-007', 'name': '文件下载功能', 'module': '文件管理', 'priority': 'L2', 'steps': '1. 点击下载按钮\n2. 等待下载完成\n3. 检查文件', 'expected': '文件成功下载到本地', 'creator': '张三'},
        ]
        for c in cases_data:
            TestCase.objects.create(**c)
        self.stdout.write(f'  + 创建 {len(cases_data)} 个测试用例')

        # 用例集
        case_sets_data = [
            {'name': '基础功能回归集', 'description': '涵盖登录、注册、搜索等核心功能的回归用例集', 'case_ids': [1, 2, 4]},
            {'name': '性能测试用例集', 'description': '首页加载、列表滑动等性能测试用例', 'case_ids': [3]},
            {'name': 'UI 兼容性用例集', 'description': '主题切换、布局适配等 UI 相关用例', 'case_ids': [5]},
        ]
        for cs in case_sets_data:
            CaseSet.objects.create(**cs)
        self.stdout.write(f'  + 创建 {len(case_sets_data)} 个用例集')

        # 分支任务配置
        task_configs_data = [
            {'branch': branches[0], 'name': '稳定性压力测试', 'script_path': 'scripts/stress_test.py', 'device_limit': 'SN001,SN002', 'case_sets': [1], 'order': 1},
            {'branch': branches[0], 'name': '功能回归测试', 'script_path': 'scripts/regression.py', 'device_limit': 'SN001', 'case_sets': [1, 3], 'order': 2},
            {'branch': branches[1], 'name': '主干全量回归', 'script_path': 'scripts/full_regression.py', 'device_limit': '', 'case_sets': [1, 2, 3], 'order': 1},
        ]
        for tc in task_configs_data:
            TaskConfig.objects.create(**tc)
        self.stdout.write(f'  + 创建 {len(task_configs_data)} 个任务配置')

        # 执行器
        executors_data = [
            {'name': '执行器-01', 'ip': '192.168.1.101', 'port': 5555, 'status': 'online', 'device_serial': 'SN001', 'last_heartbeat': datetime.now() - timedelta(minutes=1)},
            {'name': '执行器-02', 'ip': '192.168.1.102', 'port': 5555, 'status': 'online', 'device_serial': 'SN002', 'last_heartbeat': datetime.now() - timedelta(seconds=30)},
            {'name': '执行器-03', 'ip': '192.168.1.103', 'port': 5555, 'status': 'online', 'device_serial': 'SN003', 'last_heartbeat': datetime.now() - timedelta(minutes=2)},
            {'name': '执行器-04', 'ip': '192.168.1.105', 'port': 5555, 'status': 'offline', 'device_serial': 'SN005', 'last_heartbeat': datetime.now() - timedelta(hours=2)},
        ]
        for e in executors_data:
            Executor.objects.create(**e)
        self.stdout.write(f'  + 创建 {len(executors_data)} 个执行器')

        # 刷机过程
        flash_data = [
            {'device': Device.objects.get(serial='SN001'), 'branch': branches[0], 'version': 'V14.0.1', 'status': 'running',
             'steps': [
                 {'name': '下载ROM', 'status': 'completed', 'progress': 100, 'retries': 0},
                 {'name': '刷机', 'status': 'completed', 'progress': 100, 'retries': 0},
                 {'name': '开机引导', 'status': 'running', 'progress': 60, 'retries': 0},
                 {'name': '登录WiFi', 'status': 'pending', 'progress': 0, 'retries': 0},
             ]},
            {'device': Device.objects.get(serial='SN002'), 'branch': branches[0], 'version': 'V14.0.1', 'status': 'failed',
             'steps': [
                 {'name': '下载ROM', 'status': 'completed', 'progress': 100, 'retries': 0},
                 {'name': '刷机', 'status': 'failed', 'progress': 45, 'retries': 2, 'error': '刷机失败：设备断开连接'},
                 {'name': '开机引导', 'status': 'skipped', 'progress': 0, 'retries': 0},
                 {'name': '登录WiFi', 'status': 'skipped', 'progress': 0, 'retries': 0},
             ], 'retry_count': 2, 'error_message': '刷机失败：设备断开连接'},
            {'device': Device.objects.get(serial='SN003'), 'branch': branches[1], 'version': 'V15.0.0', 'status': 'completed',
             'steps': [
                 {'name': '下载ROM', 'status': 'completed', 'progress': 100, 'retries': 0},
                 {'name': '刷机', 'status': 'completed', 'progress': 100, 'retries': 1},
                 {'name': '开机引导', 'status': 'completed', 'progress': 100, 'retries': 0},
                 {'name': '登录WiFi', 'status': 'completed', 'progress': 100, 'retries': 0},
             ]},
        ]
        for f in flash_data:
            FlashingProcess.objects.create(**f)
        self.stdout.write(f'  + 创建 {len(flash_data)} 个刷机过程')

        # ROM版本记录
        rom_records_data = [
            {'branch': branches[0], 'version': 'V14.0.1.240501', 'status': 'completed', 'pass_count': 85, 'fail_count': 3, 'total_count': 88, 'pass_rate': 96.6, 'flashing_status': 'completed', 'coverage_status': 'covered'},
            {'branch': branches[0], 'version': 'V14.0.1.240425', 'status': 'completed', 'pass_count': 82, 'fail_count': 5, 'total_count': 87, 'pass_rate': 94.3, 'flashing_status': 'completed', 'coverage_status': 'covered'},
            {'branch': branches[0], 'version': 'V14.0.1.240410', 'status': 'completed', 'pass_count': 78, 'fail_count': 8, 'total_count': 86, 'pass_rate': 90.7, 'flashing_status': 'completed', 'coverage_status': 'covered'},
            {'branch': branches[1], 'version': 'V15.0.0.240501', 'status': 'running', 'pass_count': 45, 'fail_count': 2, 'total_count': 100, 'pass_rate': 45.0, 'flashing_status': 'completed', 'coverage_status': 'partial'},
            {'branch': branches[1], 'version': 'V15.0.0.240425', 'status': 'failed', 'pass_count': 30, 'fail_count': 5, 'total_count': 60, 'pass_rate': 50.0, 'flashing_status': 'failed', 'coverage_status': 'partial'},
            {'branch': branches[2], 'version': 'V14.0.5.240428', 'status': 'pending', 'pass_count': 0, 'fail_count': 0, 'total_count': 0, 'pass_rate': None, 'flashing_status': 'pending', 'coverage_status': 'uncovered'},
        ]
        for r in rom_records_data:
            RomRecord.objects.create(**r)
        self.stdout.write(f'  + 创建 {len(rom_records_data)} 个ROM版本记录')

        self.stdout.write(self.style.SUCCESS(f'种子数据初始化完成！共创建 {Device.objects.count()} 设备, {Branch.objects.count()} 分支, {Task.objects.count()} 任务, {TestCase.objects.count()} 用例, {CaseSet.objects.count()} 用例集'))
