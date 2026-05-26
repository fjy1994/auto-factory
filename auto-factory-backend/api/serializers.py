"""
序列化器
"""

from rest_framework import serializers
from .models import Device, Branch, Task, VersionQueue, TestCase, Executor, TaskConfig


class ExecutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Executor
        fields = '__all__'


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'


class TaskConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskConfig
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


# Agent上报数据序列化
class AgentReportSerializer(serializers.Serializer):
    executorId = serializers.CharField()
    executorIp = serializers.CharField()
    reportTime = serializers.DateTimeField()
    
    class DeviceItemSerializer(serializers.Serializer):
        serial = serializers.CharField()
        romVersion = serializers.CharField(default='')
        browserVersion = serializers.CharField(default='')
        executorIp = serializers.CharField(default='')
        status = serializers.CharField(default='idle')
        remark = serializers.CharField(default='', allow_blank=True)
    
    devices = DeviceItemSerializer(many=True)
