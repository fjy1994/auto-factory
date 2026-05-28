"""
REST API 视图
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Device, Branch, Task, VersionQueue, TestCase, CaseSet, TaskConfig, Executor, FlashingProcess, RomRecord
from .serializers import (
    DeviceSerializer, BranchSerializer, TaskSerializer, VersionQueueSerializer,
    TestCaseSerializer, CaseSetSerializer, TaskConfigSerializer, ExecutorSerializer,
    FlashingProcessSerializer, RomRecordSerializer, TaskStartSerializer, BatchResultSerializer,
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

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """启动任务调度：将 Task 的用例分批发送给 Agent 执行"""
        task = self.get_object()
        serializer = TaskStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        agent_url = serializer.validated_data['agent_url']
        if not task.case_ids:
            return Response({'error': '任务没有关联用例'}, status=status.HTTP_400_BAD_REQUEST)

        # 更新任务状态
        task.agent_url = agent_url
        task.status = 'running'
        task.start_time = timezone.now()
        task.current_batch = 0
        task.total_count = len(task.case_ids)
        task.case_results = []
        task.save()

        # 异步调度执行
        from .task_dispatcher import dispatch_task
        dispatch_task(task.id)

        return Response({'message': '任务调度已启动', 'task_id': task.id})

    @action(detail=False, methods=['post'])
    def report_batch(self, request):
        """Agent 回调提交批次执行结果"""
        serializer = BatchResultSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        task_id = data['task_id']
        batch_index = data['batch_index']
        results = data['results']

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response({'error': '任务不存在'}, status=status.HTTP_404_NOT_FOUND)

        # 检查批次序号是否匹配
        if batch_index != task.current_batch:
            return Response({'error': f'批次序号不匹配，期望 {task.current_batch}，收到 {batch_index}'},
                            status=status.HTTP_400_BAD_REQUEST)

        # 追加结果
        task.case_results = (task.case_results or []) + results
        task.current_batch += 1

        # 更新统计数据
        pass_count = sum(1 for r in task.case_results if r.get('status') == 'passed')
        fail_count = sum(1 for r in task.case_results if r.get('status') in ('failed', 'error'))
        task.pass_count = pass_count
        task.fail_count = fail_count
        task.progress = int(len(task.case_results) / task.total_count * 100) if task.total_count > 0 else 0
        task.pass_rate = round(pass_count / len(task.case_results) * 100, 1) if task.case_results else 0

        # 判断是否所有批次完成
        if task.current_batch * task.batch_size >= task.total_count:
            task.status = 'success'
            task.progress = 100
            task.end_time = timezone.now()

        task.save(update_fields=[
            'case_results', 'current_batch', 'pass_count', 'fail_count',
            'progress', 'pass_rate', 'status', 'end_time',
        ])

        # 如果还有下一批，继续调度
        if task.status == 'running':
            from .task_dispatcher import dispatch_task
            dispatch_task(task.id)

        return Response({
            'message': '批次结果已接收',
            'progress': task.progress,
            'status': task.status,
        })


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
