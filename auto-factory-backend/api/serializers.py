"""
REST API 序列化器
"""

from rest_framework import serializers
from .models import Device, Branch, Task, VersionQueue, TestCase, CaseSet, TaskConfig, Executor, FlashingProcess, RomRecord


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class VersionQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = VersionQueue
        fields = '__all__'


class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = '__all__'


class CaseSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseSet
        fields = '__all__'


class TaskConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskConfig
        fields = '__all__'


class ExecutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Executor
        fields = '__all__'


class FlashingProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlashingProcess
        fields = '__all__'


class RomRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RomRecord
        fields = '__all__'


class TaskStartSerializer(serializers.Serializer):
    """启动任务调度（接收 Agent 地址）"""
    agent_url = serializers.CharField(required=True, help_text='Agent 服务地址')


class BatchResultSerializer(serializers.Serializer):
    """批次结果（供 Agent 回调提交）"""
    task_id = serializers.IntegerField(required=True)
    batch_index = serializers.IntegerField(required=True)
    results = serializers.ListField(required=True, child=serializers.DictField())
