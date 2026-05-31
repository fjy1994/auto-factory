"""
数据模型 — 与设计文档（自动化工厂设计方案.md）第5章一致
所有表名使用 arkweb_ 前缀
"""

from django.db import models


class Device(models.Model):
    """5.1 arkweb_devices（设备表）"""
    serial = models.CharField(max_length=100, unique=True, verbose_name='设备序列号')
    model = models.CharField(max_length=100, blank=True, default='', verbose_name='设备型号')
    rom_version = models.CharField(max_length=100, blank=True, default='', verbose_name='当前ROM版本')
    browser_version = models.CharField(max_length=50, blank=True, default='', verbose_name='浏览器版本')
    executor_ip = models.CharField(max_length=50, blank=True, default='', verbose_name='关联执行器IP')
    status = models.CharField(max_length=20, default='idle', verbose_name='状态')
    remark = models.TextField(blank=True, default='', verbose_name='备注')
    last_report_time = models.DateTimeField(null=True, blank=True, verbose_name='上次上报时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'arkweb_devices'
        verbose_name = '设备'
        verbose_name_plural = '设备'

    def __str__(self):
        return f'{self.serial} ({self.model})'


class Branch(models.Model):
    """5.2 arkweb_branches（分支表）"""
    name = models.CharField(max_length=200, verbose_name='分支名称')
    version_pattern = models.CharField(max_length=200, blank=True, default='', verbose_name='迭代版本匹配规则')
    mail_title_pattern = models.CharField(max_length=200, blank=True, default='', verbose_name='邮件标题匹配规则')
    disabled = models.BooleanField(default=False, verbose_name='是否禁用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'arkweb_branches'
        verbose_name = '分支'
        verbose_name_plural = '分支'

    def __str__(self):
        return self.name


class Version(models.Model):
    """5.3 arkweb_versions（版本表 / 版本跟踪）"""
    class Status(models.IntegerChoices):
        NO_DEVICE = 0, '无对应设备'
        QUEUED = 1, '排队等待'
        FLASHING = 2, '刷机中'
        FLASH_FAILED = 3, '刷机失败'
        TESTING = 4, '测试中'
        COMPLETED = 5, '测试完成'
        OBSOLETED = 6, '已废弃'

    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='versions', verbose_name='所属分支')
    version = models.CharField(max_length=100, verbose_name='迭代版本号')
    status = models.IntegerField(choices=Status.choices, default=Status.NO_DEVICE, verbose_name='状态')
    pass_count = models.IntegerField(default=0, verbose_name='测试通过数')
    fail_count = models.IntegerField(default=0, verbose_name='测试失败数')
    total_count = models.IntegerField(default=0, verbose_name='总用例数')
    pass_rate = models.FloatField(null=True, blank=True, verbose_name='测试通过率')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'arkweb_versions'
        unique_together = ('branch', 'version')
        verbose_name = '迭代版本'
        verbose_name_plural = '迭代版本'

    def __str__(self):
        return f'{self.branch.name} - {self.version}'


class TaskDef(models.Model):
    """5.4 arkweb_task_defs（任务定义表）
    原 TaskConfig，重命名并调整字段以匹配设计文档
    """
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='task_defs', verbose_name='所属分支')
    name = models.CharField(max_length=200, verbose_name='任务名称')
    script_path = models.TextField(blank=True, default='', verbose_name='执行脚本路径')
    device_select_type = models.CharField(max_length=20, default='auto', verbose_name='设备选择方式')
    device_quantity = models.IntegerField(default=0, verbose_name='所需设备数')
    device_models = models.JSONField(default=list, blank=True, verbose_name='允许的机型列表')
    device_ids = models.JSONField(default=list, blank=True, verbose_name='指定设备ID列表')
    case_ids = models.JSONField(default=list, blank=True, verbose_name='关联用例ID列表')
    case_set_ids = models.JSONField(default=list, blank=True, verbose_name='关联用例集ID列表')
    batch_size = models.IntegerField(default=10, verbose_name='每批下发用例数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'arkweb_task_defs'
        verbose_name = '任务定义'
        verbose_name_plural = '任务定义'

    def __str__(self):
        return self.name


class Email(models.Model):
    """5.5 arkweb_emails（邮件表）"""
    subject = models.CharField(max_length=500, verbose_name='邮件主题')
    sender = models.CharField(max_length=200, verbose_name='发件人')
    body = models.TextField(blank=True, default='', verbose_name='邮件正文')
    received_at = models.DateTimeField(verbose_name='接收时间')
    analysis_status = models.CharField(max_length=20, default='pending', verbose_name='LLM分析状态')
    analysis_fail_count = models.IntegerField(default=0, verbose_name='分析失败次数')
    extracted_branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='emails', verbose_name='关联分支')
    extracted_version = models.CharField(max_length=100, blank=True, default='', verbose_name='迭代版本号')
    extracted_roms = models.JSONField(default=list, blank=True, verbose_name='转测ROM列表')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'arkweb_emails'
        verbose_name = '邮件'
        verbose_name_plural = '邮件'

    def __str__(self):
        return self.subject[:50]


class FlashingTask(models.Model):
    """5.6 arkweb_flashing_tasks（刷机任务表）— 版本维度的刷机任务，1:1 关联 Version"""
    version = models.OneToOneField(Version, on_delete=models.CASCADE, related_name='flashing_task', verbose_name='关联版本')
    status = models.CharField(max_length=20, default='pending', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'arkweb_flashing_tasks'
        verbose_name = '刷机任务'
        verbose_name_plural = '刷机任务'

    def __str__(self):
        return f'FlashingTask-{self.version.version}'


class FlashingProcess(models.Model):
    """5.7 arkweb_flashing_processes（刷机过程表）— 每设备一条记录，关联刷机任务"""
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='flashing_processes', verbose_name='刷机设备')
    flashing_task = models.ForeignKey(FlashingTask, on_delete=models.CASCADE, null=True, blank=True, related_name='processes', verbose_name='关联刷机任务')
    rom = models.CharField(max_length=200, blank=True, default='', verbose_name='刷机ROM版本号')
    status = models.CharField(max_length=20, default='pending', verbose_name='总体状态')
    steps = models.JSONField(default=list, blank=True, verbose_name='步骤状态列表')
    retry_count = models.IntegerField(default=0, verbose_name='已重试总次数')
    error_message = models.TextField(blank=True, default='', verbose_name='总体错误信息')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'arkweb_flashing_processes'
        verbose_name = '刷机过程'
        verbose_name_plural = '刷机过程'

    def __str__(self):
        return f'{self.device.serial} - {self.version_info()}'

    def version_info(self):
        return self.flashing_task.version.version if self.flashing_task_id else '?'


class Task(models.Model):
    """5.7 arkweb_tasks（任务表 / 任务中心）"""
    name = models.CharField(max_length=200, verbose_name='任务名称')
    task_def = models.ForeignKey(TaskDef, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks', verbose_name='关联任务定义')
    version = models.ForeignKey(Version, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks', verbose_name='关联迭代版本')
    status = models.CharField(max_length=20, default='queued', verbose_name='状态')
    progress = models.IntegerField(default=0, verbose_name='执行进度百分比')
    pass_rate = models.FloatField(null=True, blank=True, verbose_name='通过率')
    total_count = models.IntegerField(default=0, verbose_name='总用例数')
    pass_count = models.IntegerField(default=0, verbose_name='通过数')
    fail_count = models.IntegerField(default=0, verbose_name='失败数')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'arkweb_tasks'
        verbose_name = '任务'
        verbose_name_plural = '任务'

    def __str__(self):
        return self.name


class TestCase(models.Model):
    """5.8 arkweb_test_cases（测试用例表）"""
    case_id = models.CharField(max_length=50, unique=True, verbose_name='用例编号')
    name = models.CharField(max_length=200, verbose_name='用例名称')
    module = models.CharField(max_length=100, blank=True, default='', verbose_name='所属模块')
    priority = models.CharField(max_length=20, default='L2', verbose_name='优先级')
    precondition = models.TextField(blank=True, default='', verbose_name='前置步骤')
    script_path = models.CharField(max_length=500, blank=True, default='', verbose_name='脚本路径')
    steps = models.TextField(blank=True, default='', verbose_name='测试步骤')
    expected = models.TextField(blank=True, default='', verbose_name='预期结果')
    creator = models.CharField(max_length=100, blank=True, default='', verbose_name='责任人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'arkweb_test_cases'
        verbose_name = '测试用例'
        verbose_name_plural = '测试用例'

    def __str__(self):
        return f'[{self.case_id}] {self.name}'


class CaseSet(models.Model):
    """5.9 arkweb_test_case_sets（用例集表）"""
    name = models.CharField(max_length=200, verbose_name='用例集名称')
    description = models.TextField(blank=True, default='', verbose_name='描述')
    case_ids = models.JSONField(default=list, blank=True, verbose_name='用例ID列表')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'arkweb_test_case_sets'
        verbose_name = '用例集'
        verbose_name_plural = '用例集'

    def __str__(self):
        return self.name


class TaskResult(models.Model):
    """5.10 arkweb_task_results（用例执行结果表）"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='results', verbose_name='所属任务')
    case_id = models.CharField(max_length=50, verbose_name='用例编号')
    status = models.CharField(max_length=20, verbose_name='状态')
    error_message = models.TextField(blank=True, default='', verbose_name='错误信息')
    duration = models.IntegerField(null=True, blank=True, verbose_name='执行耗时(秒)')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='开始执行时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束执行时间')

    class Meta:
        db_table = 'arkweb_task_results'
        verbose_name = '用例执行结果'
        verbose_name_plural = '用例执行结果'

    def __str__(self):
        return f'Task {self.task_id} - {self.case_id}'
