"""
Django Admin 配置
"""

from django.contrib import admin
from .models import Device, Branch, Task, VersionQueue, TestCase, Executor


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['serial', 'rom_version', 'browser_version', 'executor_ip', 'status', 'last_report_time']
    list_filter = ['status', 'executor_ip']
    search_fields = ['serial', 'rom_version', 'browser_version']


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'version_pattern', 'disabled', 'created_at']
    list_filter = ['disabled']
    search_fields = ['name']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'branch_name', 'version', 'status', 'progress', 'device_serial', 'created_at']
    list_filter = ['status', 'branch_name', 'task_type']
    search_fields = ['name', 'version', 'device_serial']


@admin.register(VersionQueue)
class VersionQueueAdmin(admin.ModelAdmin):
    list_display = ['version', 'branch_name', 'status', 'reason', 'received_at']
    list_filter = ['status']
    search_fields = ['version', 'branch_name']


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ['case_id', 'name', 'module', 'priority', 'creator', 'created_at']
    list_filter = ['module', 'priority']
    search_fields = ['case_id', 'name']


@admin.register(Executor)
class ExecutorAdmin(admin.ModelAdmin):
    list_display = ['executor_id', 'executor_ip', 'status', 'last_heartbeat', 'created_at']
    list_filter = ['status']
    search_fields = ['executor_id', 'executor_ip']
