"""
URL configuration for auto-factory-backend project.
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views

router = DefaultRouter()

# 设备
router.register(r'devices', views.DeviceViewSet)

# 分支
router.register(r'branches', views.BranchViewSet)

# 任务
router.register(r'tasks', views.TaskViewSet)

# 待执行队列
router.register(r'version-queue', views.VersionQueueViewSet)

# 测试用例
router.register(r'test-cases', views.TestCaseViewSet)

# 执行机
router.register(r'executors', views.ExecutorViewSet)

# 分支任务配置
router.register(r'task-configs', views.TaskConfigViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    
    # 其他接口
    path('api/v1/health/', views.health_check),
    path('api/v1/agent/report/', views.agent_report),
    path('api/v1/test-cases/modules/', views.get_modules),
    path('api/v1/devices/<str:serial>/reboot/', views.device_reboot),
    path('api/v1/agent/<str:executor_id>/command/', views.send_command),
    path('api/v1/tasks/<int:pk>/cancel/', views.cancel_task),
    path('api/v1/tasks/<int:pk>/rerun/', views.rerun_task),
    path('api/v1/version-queue/<int:pk>/create-tasks/', views.create_tasks_from_queue),
]
