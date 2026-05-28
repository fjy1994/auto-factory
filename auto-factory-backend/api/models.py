"""
数据库模型定义
"""

from django.db import models


class Device(models.Model):
    """设备"""
    serial = models.CharField(max_length=100, unique=True, verbose_name='序列号')
    device_name = models.CharField(max_length=200, blank=True, default='', verbose_name='设备名称')
    model = models.CharField(max_length=100, blank=True, default='', verbose_name='设备型号')
    rom_version = models.CharField(max_length=100, blank=True, default='', verbose_name='ROM版本')
    browser_version = models.CharField(max_length=50, blank=True, default='', verbose_name='浏览器版本')
    executor_ip = models.CharField(max_length=50, blank=True, default='', verbose_name='执行器IP')
    status = models.CharField(max_length=20, default='idle', verbose_name='状态')
    remark = models.TextField(blank=True, default='', verbose_name='备注')
    last_report_time = models.DateTimeField(null=True, blank=True, verbose_name='上次上报时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'devices'
        verbose_name = '设备'
        verbose_name_plural = '设备'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.serial} - {self.device_name or self.model}'


class Branch(models.Model):
    """ROM分支"""
    name = models.CharField(max_length=200, verbose_name='分支名称')
    type = models.CharField(max_length=50, blank=True, default='', verbose_name='类型(DEV/主干/商分)')
    version = models.CharField(max_length=100, blank=True, default='', verbose_name='版本号')
    model = models.CharField(max_length=100, blank=True, default='', verbose_name='机型')
    version_pattern = models.CharField(max_length=200, blank=True, default='', verbose_name='版本匹配规则')
    mail_title_pattern = models.CharField(max_length=200, blank=True, default='', verbose_name='邮件标题匹配规则')
    disabled = models.BooleanField(default=False, verbose_name='是否禁用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'branches'
        verbose_name = 'ROM分支'
        verbose_name_plural = 'ROM分支'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Task(models.Model):
    """任务"""
    name = models.CharField(max_length=200, verbose_name='任务名称')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True, verbose_name='所属分支')
    branch_name = models.CharField(max_length=200, blank=True, default='', verbose_name='分支名称(冗余)')
    version = models.CharField(max_length=100, blank=True, default='', verbose_name='版本号')
    model = models.CharField(max_length=100, blank=True, default='', verbose_name='机型')
    task_type = models.CharField(max_length=50, blank=True, default='', verbose_name='任务类型')
    status = models.CharField(max_length=20, default='queued', verbose_name='状态')
    progress = models.IntegerField(default=0, verbose_name='进度')
    device_serial = models.CharField(max_length=100, blank=True, default='', verbose_name='设备序列号')
    agent_url = models.CharField(max_length=500, blank=True, default='', verbose_name='Agent地址')
    case_ids = models.JSONField(default=list, verbose_name='关联用例ID列表')
    batch_size = models.IntegerField(default=10, verbose_name='每批下发数量')
    current_batch = models.IntegerField(default=0, verbose_name='当前批次序号')
    case_results = models.JSONField(default=list, verbose_name='用例执行结果')
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
        verbose_name_plural = '任务'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class VersionQueue(models.Model):
    """版本队列"""
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='version_queue', verbose_name='分支')
    version = models.CharField(max_length=100, verbose_name='版本号')
    status = models.CharField(max_length=20, default='pending', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'version_queue'
        verbose_name = '版本队列'
        verbose_name_plural = '版本队列'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.branch.name} - {self.version}'


class TestCase(models.Model):
    """测试用例"""
    case_id = models.CharField(max_length=50, unique=True, verbose_name='用例编号')
    name = models.CharField(max_length=200, verbose_name='用例名称')
    module = models.CharField(max_length=100, blank=True, default='', verbose_name='所属模块')
    priority = models.CharField(max_length=20, default='L2', verbose_name='优先级')
    script_path = models.CharField(max_length=500, blank=True, default='', verbose_name='脚本路径')
    steps = models.TextField(blank=True, default='', verbose_name='测试步骤')
    expected = models.TextField(blank=True, default='', verbose_name='预期结果')
    creator = models.CharField(max_length=100, blank=True, default='', verbose_name='责任人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'test_cases'
        verbose_name = '测试用例'
        verbose_name_plural = '测试用例'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.case_id} - {self.name}'


class CaseSet(models.Model):
    """用例集"""
    name = models.CharField(max_length=200, verbose_name='用例集名称')
    description = models.TextField(blank=True, default='', verbose_name='描述')
    case_ids = models.JSONField(default=list, verbose_name='包含用例ID列表')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'case_sets'
        verbose_name = '用例集'
        verbose_name_plural = '用例集'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class TaskConfig(models.Model):
    """分支任务配置"""
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='task_configs', verbose_name='所属分支')
    name = models.CharField(max_length=200, verbose_name='配置名称')
    script_path = models.TextField(blank=True, default='', verbose_name='脚本路径')
    device_limit = models.CharField(max_length=50, blank=True, default='', verbose_name='设备限制')
    case_sets = models.JSONField(default=list, verbose_name='关联用例集ID列表')
    batch_size = models.IntegerField(default=10, verbose_name='每批下发数量')
    order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'task_configs'
        verbose_name = '分支任务配置'
        verbose_name_plural = '分支任务配置'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.branch.name} - {self.name}'


class Executor(models.Model):
    """执行器"""
    name = models.CharField(max_length=100, verbose_name='执行器名称')
    ip = models.CharField(max_length=50, verbose_name='IP地址')
    port = models.IntegerField(default=5555, verbose_name='端口')
    status = models.CharField(max_length=20, default='offline', verbose_name='状态')
    device_serial = models.CharField(max_length=100, blank=True, default='', verbose_name='关联设备序列号')
    last_heartbeat = models.DateTimeField(null=True, blank=True, verbose_name='上次心跳')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'executors'
        verbose_name = '执行器'
        verbose_name_plural = '执行器'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class FlashingProcess(models.Model):
    """刷机过程"""
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='flashing_processes', verbose_name='设备')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='flashing_processes', verbose_name='分支')
    version = models.CharField(max_length=100, blank=True, default='', verbose_name='版本号')
    status = models.CharField(max_length=20, default='pending', verbose_name='总体状态')
    steps = models.JSONField(default=list, verbose_name='步骤状态列表')
    retry_count = models.IntegerField(default=0, verbose_name='已重试次数')
    error_message = models.TextField(blank=True, default='', verbose_name='错误信息')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'flashing_processes'
        verbose_name = '刷机过程'
        verbose_name_plural = '刷机过程'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.device.serial} - {self.version}'


class RomRecord(models.Model):
    """ROM版本记录"""
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='rom_records', verbose_name='分支')
    version = models.CharField(max_length=100, verbose_name='版本号')
    status = models.CharField(max_length=20, default='pending', verbose_name='状态')
    pass_count = models.IntegerField(default=0, verbose_name='通过数')
    fail_count = models.IntegerField(default=0, verbose_name='失败数')
    total_count = models.IntegerField(default=0, verbose_name='总用例数')
    pass_rate = models.FloatField(null=True, blank=True, verbose_name='通过率')
    flashing_status = models.CharField(max_length=50, blank=True, default='', verbose_name='刷机状态')
    coverage_status = models.CharField(max_length=50, blank=True, default='', verbose_name='覆盖状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'rom_records'
        verbose_name = 'ROM版本记录'
        verbose_name_plural = 'ROM版本记录'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.branch.name} - {self.version}'
