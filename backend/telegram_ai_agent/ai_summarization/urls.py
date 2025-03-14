from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SummaryViewSet, SummaryFeedbackViewSet

router = DefaultRouter()
router.register(r'summaries', SummaryViewSet, basename='summary')
router.register(r'feedback', SummaryFeedbackViewSet, basename='summary-feedback')

urlpatterns = [
    path('', include(router.urls)),
]
