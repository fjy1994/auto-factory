"""
视图函数
"""

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Device, Branch, Task, VersionQueue, TestCase, Executor, TaskConfig
from .serializers import (
    DeviceSerializer, BranchSerializer, TaskSerializer,
    VersionQueueSerializer, TestCaseSerializer, ExecutorSerializer,
    AgentReportSerializer, TaskConfigSerializer
)
from .consumers import send_command_to_agent


# ============= 健康检查 =============

@api_view(['GET'])
def health_check(request):
    return Response({
        'status': 'ok',
        'timestamp': timezone.now().isoformat()
    })


# ============= Agent上报 =============

@api_view(['POST'])
def agent_report(request):
    """Agent上报设备信息"""
    serializer = AgentReportSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    data = serializer.validated_data
    executor_id = data['executorId']
    executor_ip = data['executorIp']
    
    # 更新或创建执行机
    Executor.objects.update_or_create(
        executor_id=executor_id,
        defaults={
            'executor_ip': executor_ip,
            'status': 'online',
        }
    )
    
    # 更新设备信息
    for device_data in data['devices']:
        Device.objects.update_or_create(
            serial=device_data['serial'],
            defaults={
                'rom_version': device_data.get('romVersion', ''),
                'browser_version': device_data.get('browserVersion', ''),
                'executor_ip': device_data.get('executorIp', executor_ip),
                'status': device_data.get('status', 'idle'),
                'last_report_time': timezone.now(),
            }
        )
    
    return Response({
        'code': 0,
        'message': '上报成功',
        'device_count': len(data['devices'])
    })


# ============= 设备管理 =============

class DeviceViewSet(viewsets.ModelViewSet):
    """设备管理"""
    queryset = Device.objects.all().order_by('-last_report_time')
    serializer_class = DeviceSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset


@api_view(['POST'])
def device_reboot(request, serial):
    """远程重启设备"""
    device = get_object_or_404(Device, serial=serial)
    
    # 通过WebSocket下发重启指令
    success = send_command_to_agent(device.executor_ip, {
        'command': 'reboot',
        'deviceSerial': serial,
    })
    
    if success:
        return Response({'code': 0, 'message': '重启指令已下发'})
    else:
        return Response(
            {'code': 1, 'message': 'Agent不在线，指令发送失败'},
            status=status.HTTP_400_BAD_REQUEST
        )


# ============= 分支管理 =============

class BranchViewSet(viewsets.ModelViewSet):
    """分支管理"""
    queryset = Branch.objects.all().order_by('-created_at')
    serializer_class = BranchSerializer


# ============= 任务管理 =============

class TaskViewSet(viewsets.ModelViewSet):
    """任务管理"""
    queryset = Task.objects.all().order_by('-created_at')
    serializer_class = TaskSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        branch_id = self.request.query_params.get('branchId')
        if status:
            queryset = queryset.filter(status=status)
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        return queryset[:100]


@api_view(['PUT'])
def cancel_task(request, pk):
    """取消任务"""
    task = get_object_or_404(Task, pk=pk)
    if task.status in ['queued', 'running']:
        task.status = 'cancelled'
        task.save()
        return Response({'code': 0, 'message': '任务已取消'})
    return Response(
        {'code': 1, 'message': '该任务状态不允许取消'},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['PUT'])
def rerun_task(request, pk):
    """重跑任务"""
    task = get_object_or_404(Task, pk=pk)
    task.status = 'queued'
    task.progress = 0
    task.start_time = None
    task.end_time = None
    task.save()
    return Response({'code': 0, 'message': '任务已重排'})


# ============= 待执行队列 =============

class VersionQueueViewSet(viewsets.ModelViewSet):
    """待执行版本队列"""
    queryset = VersionQueue.objects.all().order_by('-received_at')
    serializer_class = VersionQueueSerializer


@api_view(['POST'])
def create_tasks_from_queue(request, pk):
    """从待执行队列创建任务"""
    item = get_object_or_404(VersionQueue, pk=pk)
    
    # 创建任务
    Task.objects.create(
        name=f'{item.version} - 自动化测试',
        branch=item.branch,
        branch_name=item.branch_name,
        version=item.version,
        status='queued',
    )
    
    # 删除队列项
    item.delete()
    
    return Response({'code': 0, 'message': '任务已创建'})


# ============= 测试用例 =============

class TestCaseViewSet(viewsets.ModelViewSet):
    """测试用例管理"""
    queryset = TestCase.objects.all().order_by('-created_at')
    serializer_class = TestCaseSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        module = self.request.query_params.get('module')
        priority = self.request.query_params.get('priority')
        keyword = self.request.query_params.get('keyword')
        
        if module:
            queryset = queryset.filter(module=module)
        if priority:
            queryset = queryset.filter(priority=priority)
        if keyword:
            queryset = queryset.filter(
                models.Q(name__icontains=keyword) |
                models.Q(case_id__icontains=keyword)
            )
        return queryset[:500]


@api_view(['GET'])
def get_modules(request):
    """获取所有模块列表"""
    modules = TestCase.objects.exclude(module='').values_list('module', flat=True).distinct()
    return Response({'code': 0, 'data': list(modules)})


# ============= 执行机管理 =============

class ExecutorViewSet(viewsets.ModelViewSet):
    """执行机管理"""
    queryset = Executor.objects.all().order_by('-last_heartbeat')
    serializer_class = ExecutorSerializer


@api_view(['POST'])
def send_command(request, executor_id):
    """向指定Agent下发指令"""
    success = send_command_to_agent(executor_id, request.data)
    if success:
        return Response({'code': 0, 'message': '指令已发送'})
    return Response(
        {'code': 1, 'message': 'Agent不在线'},
        status=status.HTTP_404_NOT_FOUND
    )


# ============= 分支任务配置管理 =============

class TaskConfigViewSet(viewsets.ModelViewSet):
    """分支任务配置管理"""
    queryset = TaskConfig.objects.all().order_by('-created_at')
    serializer_class = TaskConfigSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        branch_id = self.request.query_params.get('branch_id')
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        return queryset


# 导入models避免循环导入
from django.db import models
