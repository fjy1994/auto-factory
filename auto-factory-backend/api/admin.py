"""
Admin配置
"""

from django.contrib import admin
from .models import (
    Device, Branch, Version, TaskDef, Email,
    FlashingTask, FlashingProcess,
    Task, TestCase, CaseSet, TaskResult,
)


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('id', 'serial', 'model', 'status', 'rom_version', 'executor_ip', 'created_at')
    list_filter = ('status',)
    search_fields = ('serial', 'model')


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'version_pattern', 'disabled', 'created_at')
    list_filter = ('disabled',)
    search_fields = ('name',)


@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    list_display = ('id', 'branch', 'version', 'status', 'pass_count', 'fail_count', 'pass_rate', 'created_at')
    list_filter = ('status',)
    search_fields = ('version', 'branch__name')


@admin.register(TaskDef)
class TaskDefAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'branch', 'device_select_type', 'device_quantity', 'batch_size', 'created_at')
    search_fields = ('name',)
    list_filter = ('device_select_type',)


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'sender', 'received_at', 'analysis_status', 'extracted_version')
    list_filter = ('analysis_status',)
    search_fields = ('subject', 'sender', 'extracted_version')


@admin.register(FlashingTask)
class FlashingTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'version', 'status', 'created_at')
    list_filter = ('status',)


@admin.register(FlashingProcess)
class FlashingProcessAdmin(admin.ModelAdmin):
    list_display = ('id', 'device', 'flashing_task', 'rom', 'status', 'retry_count', 'created_at')
    list_filter = ('status',)
    search_fields = ('device__serial',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'task_def', 'version', 'status', 'progress', 'pass_rate', 'created_at')
    list_filter = ('status',)
    search_fields = ('name',)


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'case_id', 'name', 'module', 'priority', 'creator', 'created_at')
    list_filter = ('priority', 'module')
    search_fields = ('case_id', 'name', 'module')


@admin.register(CaseSet)
class CaseSetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)


@admin.register(TaskResult)
class TaskResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'case_id', 'status', 'duration')
    list_filter = ('status',)
