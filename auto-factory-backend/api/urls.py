"""
REST API 路由配置 — 所有 URL 以 /arkweb 为前缀
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'devices', views.DeviceViewSet)
router.register(r'branches', views.BranchViewSet)
router.register(r'task-defs', views.TaskDefViewSet)
router.register(r'versions', views.VersionViewSet)
router.register(r'flashing', views.FlashingProcessViewSet)
router.register(r'flashing-tasks', views.FlashingTaskViewSet)
router.register(r'tasks', views.TaskViewSet)
router.register(r'test-cases', views.TestCaseViewSet)
router.register(r'case-sets', views.CaseSetViewSet)
router.register(r'emails', views.EmailViewSet)

urlpatterns = [
    path('arkweb/', include(router.urls)),
    path('arkweb/dashboard/stats', views.dashboard_stats, name='dashboard-stats'),
]
