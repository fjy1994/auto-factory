"""
REST API 路由配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'devices', views.DeviceViewSet)
router.register(r'branches', views.BranchViewSet)
router.register(r'tasks', views.TaskViewSet)
router.register(r'version-queue', views.VersionQueueViewSet)
router.register(r'test-cases', views.TestCaseViewSet)
router.register(r'case-sets', views.CaseSetViewSet)
router.register(r'task-configs', views.TaskConfigViewSet)
router.register(r'executors', views.ExecutorViewSet)
router.register(r'flashing-processes', views.FlashingProcessViewSet)
router.register(r'rom-records', views.RomRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
