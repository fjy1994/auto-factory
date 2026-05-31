"""
REST API 序列化器
"""

from rest_framework import serializers
from .models import (
    Device, Branch, Version, TaskDef, Email,
    FlashingTask, FlashingProcess,
    Task, TestCase, CaseSet, TaskResult,
)


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'


class VersionSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    flashing_task_id = serializers.SerializerMethodField()

    class Meta:
        model = Version
        fields = '__all__'

    def get_flashing_task_id(self, obj):
        try:
            return obj.flashing_task.id
        except FlashingTask.DoesNotExist:
            return None


class FlashingTaskSerializer(serializers.ModelSerializer):
    version_label = serializers.CharField(source='version.version', read_only=True)
    branch_name = serializers.CharField(source='version.branch.name', read_only=True)
    processes = serializers.SerializerMethodField()

    class Meta:
        model = FlashingTask
        fields = '__all__'

    def get_processes(self, obj):
        processes = obj.processes.all()
        return FlashingProcessSerializer(processes, many=True).data


class TaskDefSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskDef
        fields = '__all__'


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = '__all__'


class FlashingProcessSerializer(serializers.ModelSerializer):
    device_serial = serializers.CharField(source='device.serial', read_only=True)
    device_model = serializers.CharField(source='device.model', read_only=True)
    version_label = serializers.CharField(source='flashing_task.version.version', read_only=True)
    flashing_task_id = serializers.IntegerField(source='flashing_task.id', read_only=True)

    class Meta:
        model = FlashingProcess
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    task_def_name = serializers.CharField(source='task_def.name', read_only=True)
    version_label = serializers.CharField(source='version.version', read_only=True)
    branch_name = serializers.CharField(source='version.branch.name', read_only=True)

    class Meta:
        model = Task
        fields = '__all__'


class TaskResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskResult
        fields = '__all__'


class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = '__all__'


class CaseSetSerializer(serializers.ModelSerializer):
    case_count = serializers.SerializerMethodField()

    class Meta:
        model = CaseSet
        fields = '__all__'

    def get_case_count(self, obj):
        return len(obj.case_ids or [])
