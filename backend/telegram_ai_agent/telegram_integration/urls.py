from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TelegramAccountViewSet,
    TelegramGroupViewSet,
    TelegramMessageViewSet,
    AccountGroupAssociationViewSet
)

router = DefaultRouter()
router.register(r'accounts', TelegramAccountViewSet, basename='telegram-account')
router.register(r'groups', TelegramGroupViewSet, basename='telegram-group')
router.register(r'messages', TelegramMessageViewSet, basename='telegram-message')
router.register(r'associations', AccountGroupAssociationViewSet, basename='account-group-association')

urlpatterns = [
    path('', include(router.urls)),
]
