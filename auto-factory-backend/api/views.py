"""
REST API 视图
"""

from rest_framework import viewsets, filters
from .models import Device, Branch, Task, VersionQueue, TestCase, CaseSet, TaskConfig, Executor, FlashingProcess, RomRecord
from .serializers import (
    DeviceSerializer, BranchSerializer, TaskSerializer, VersionQueueSerializer,
    TestCaseSerializer, CaseSetSerializer, TaskConfigSerializer, ExecutorSerializer,
    FlashingProcessSerializer, RomRecordSerializer,
)


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['serial', 'device_name', 'model']
    ordering_fields = ['created_at', 'serial', 'status']


class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'type', 'version']
    ordering_fields = ['created_at', 'name']


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'branch_name', 'version', 'status']
    ordering_fields = ['created_at', 'start_time', 'status']


class VersionQueueViewSet(viewsets.ModelViewSet):
    queryset = VersionQueue.objects.all()
    serializer_class = VersionQueueSerializer


class TestCaseViewSet(viewsets.ModelViewSet):
    queryset = TestCase.objects.all()
    serializer_class = TestCaseSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['case_id', 'name', 'module']
    ordering_fields = ['created_at', 'priority']


class CaseSetViewSet(viewsets.ModelViewSet):
    queryset = CaseSet.objects.all()
    serializer_class = CaseSetSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']


class TaskConfigViewSet(viewsets.ModelViewSet):
    queryset = TaskConfig.objects.all()
    serializer_class = TaskConfigSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class ExecutorViewSet(viewsets.ModelViewSet):
    queryset = Executor.objects.all()
    serializer_class = ExecutorSerializer


class FlashingProcessViewSet(viewsets.ModelViewSet):
    queryset = FlashingProcess.objects.all()
    serializer_class = FlashingProcessSerializer
    ordering_fields = ['created_at', 'updated_at']


class RomRecordViewSet(viewsets.ModelViewSet):
    queryset = RomRecord.objects.all()
    serializer_class = RomRecordSerializer
    ordering_fields = ['created_at', 'version', 'pass_rate']
