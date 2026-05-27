"""
Admin配置
"""

from django.contrib import admin
from .models import Device, Branch, Task, VersionQueue, TestCase, CaseSet, TaskConfig, Executor, FlashingProcess, RomRecord


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('id', 'serial', 'device_name', 'model', 'status', 'rom_version', 'created_at')
    list_filter = ('status',)
    search_fields = ('serial', 'device_name', 'model')


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'version', 'model', 'disabled', 'created_at')
    list_filter = ('type', 'disabled')
    search_fields = ('name', 'type', 'version')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'branch_name', 'version', 'task_type', 'status', 'created_at')
    list_filter = ('status', 'task_type')
    search_fields = ('name', 'branch_name', 'version')


@admin.register(VersionQueue)
class VersionQueueAdmin(admin.ModelAdmin):
    list_display = ('id', 'branch', 'version', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('version',)


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'case_id', 'name', 'module', 'priority', 'creator', 'created_at')
    list_filter = ('priority', 'module')
    search_fields = ('case_id', 'name', 'module')


@admin.register(CaseSet)
class CaseSetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)


@admin.register(TaskConfig)
class TaskConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'branch', 'created_at')
    search_fields = ('name',)


@admin.register(Executor)
class ExecutorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'ip', 'status', 'last_heartbeat', 'created_at')
    list_filter = ('status',)


@admin.register(FlashingProcess)
class FlashingProcessAdmin(admin.ModelAdmin):
    list_display = ('id', 'device', 'branch', 'version', 'status', 'retry_count', 'created_at')
    list_filter = ('status',)


@admin.register(RomRecord)
class RomRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'branch', 'version', 'status', 'pass_rate', 'created_at')
    list_filter = ('status', 'coverage_status')
