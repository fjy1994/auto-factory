"""
数据库模型
"""

from django.db import models


class Executor(models.Model):
    """执行机"""
    executor_id = models.CharField(max_length=100, unique=True, verbose_name='执行机ID')
    executor_ip = models.CharField(max_length=50, verbose_name='执行机IP')
    status = models.CharField(max_length=20, default='online', verbose_name='状态')
    last_heartbeat = models.DateTimeField(auto_now=True, verbose_name='最后心跳')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'executors'
        verbose_name = '执行机'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.executor_id


class Device(models.Model):
    """设备"""
    STATUS_CHOICES = [
        ('idle', '空闲'),
        ('busy', '忙碌'),
        ('flashing', '刷机中'),
        ('offline', '离线'),
        ('error', '异常'),
    ]

    serial = models.CharField(max_length=100, unique=True, verbose_name='设备序列号')
    rom_version = models.CharField(max_length=100, default='', verbose_name='ROM版本')
    browser_version = models.CharField(max_length=100, default='', verbose_name='浏览器版本')
    executor_ip = models.CharField(max_length=50, default='', verbose_name='所在执行机IP')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline', verbose_name='状态')
    remark = models.TextField(default='', blank=True, verbose_name='备注')
    last_report_time = models.DateTimeField(auto_now=True, verbose_name='最后上报时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'devices'
        verbose_name = '设备'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.serial


class Branch(models.Model):
    """分支"""
    name = models.CharField(max_length=100, unique=True, verbose_name='分支名称')
    version_pattern = models.CharField(max_length=200, verbose_name='版本匹配规则')
    disabled = models.BooleanField(default=False, verbose_name='是否禁用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'branches'
        verbose_name = '分支'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Task(models.Model):
    """任务"""
    STATUS_CHOICES = [
        ('queued', '排队中'),
        ('running', '执行中'),
        ('success', '成功'),
        ('failed', '失败'),
        ('cancelled', '已取消'),
        ('error', '异常'),
    ]

    name = models.CharField(max_length=200, verbose_name='任务名称')
    branch = models.ForeignKey(Branch, null=True, on_delete=models.SET_NULL, verbose_name='所属分支')
    branch_name = models.CharField(max_length=100, default='', verbose_name='分支名称')
    version = models.CharField(max_length=100, default='', verbose_name='版本号')
    model = models.CharField(max_length=100, default='', verbose_name='机型')
    task_type = models.CharField(max_length=50, default='auto', verbose_name='任务类型')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued', verbose_name='状态')
    progress = models.IntegerField(default=0, verbose_name='进度')
    device_serial = models.CharField(max_length=100, default='', verbose_name='执行设备序列号')
    pass_rate = models.FloatField(null=True, blank=True, verbose_name='通过率')
    total_count = models.IntegerField(default=0, verbose_name='总用例数')
    pass_count = models.IntegerField(default=0, verbose_name='通过数')
    fail_count = models.IntegerField(default=0, verbose_name='失败数')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tasks'
        verbose_name = '任务'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class VersionQueue(models.Model):
    """待执行版本队列"""
    STATUS_CHOICES = [
        ('waiting_rom', '等待ROM'),
        ('waiting_device', '等待设备'),
        ('pending', '待执行'),
        ('processed', '已处理'),
    ]

    branch = models.ForeignKey(Branch, null=True, on_delete=models.SET_NULL, verbose_name='所属分支')
    branch_name = models.CharField(max_length=100, default='', verbose_name='分支名称')
    version = models.CharField(max_length=100, verbose_name='版本号')
    models_str = models.CharField(max_length=200, default='', verbose_name='目标机型')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    reason = models.TextField(default='', blank=True, verbose_name='原因说明')
    received_at = models.DateTimeField(auto_now_add=True, verbose_name='接收时间')

    class Meta:
        db_table = 'version_queue'
        verbose_name = '待执行版本队列'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.version


class TestCase(models.Model):
    """测试用例"""
    PRIORITY_CHOICES = [
        ('high', '高'),
        ('medium', '中'),
        ('low', '低'),
    ]

    case_id = models.CharField(max_length=100, unique=True, verbose_name='用例ID')
    name = models.CharField(max_length=200, verbose_name='用例名称')
    module = models.CharField(max_length=100, default='', blank=True, verbose_name='所属模块')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name='优先级')
    steps = models.TextField(default='', blank=True, verbose_name='测试步骤')
    expected = models.TextField(default='', blank=True, verbose_name='预期结果')
    creator = models.CharField(max_length=50, default='system', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'test_cases'
        verbose_name = '测试用例'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.case_id


class TaskConfig(models.Model):
    """分支任务配置"""
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='task_configs', verbose_name='所属分支')
    name = models.CharField(max_length=200, verbose_name='任务名称')
    script_path = models.CharField(max_length=500, default='', blank=True, verbose_name='脚本路径')
    min_device_count = models.IntegerField(default=1, verbose_name='最少设备数')
    max_device_count = models.IntegerField(default=3, verbose_name='最大设备数')
    case_pattern = models.CharField(max_length=500, default='', blank=True, verbose_name='用例匹配规则')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'task_configs'
        verbose_name = '分支任务配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
