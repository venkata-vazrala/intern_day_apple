from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PipelineViewSet, RunViewSet
from .views_ui import PipelineListView, PipelineDashboardView

router = DefaultRouter()
router.register(r'pipelines', PipelineViewSet, basename='pipeline')
router.register(r'runs', RunViewSet, basename='run')

urlpatterns = [
    # Simple HTML dashboard pages
    path('', PipelineListView.as_view(), name='pipeline_list'),
    path('pipelines/<int:pk>/', PipelineDashboardView.as_view(), name='pipeline_dashboard'),
    path('api/', include(router.urls)),
]
