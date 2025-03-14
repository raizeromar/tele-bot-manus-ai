from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import UserViewSet
from telegram_integration.views import (
    TelegramAccountViewSet,
    TelegramGroupViewSet,
    TelegramMessageViewSet,
    AccountGroupAssociationViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'telegram/accounts', TelegramAccountViewSet, basename='telegram-account')
router.register(r'telegram/groups', TelegramGroupViewSet, basename='telegram-group')
router.register(r'telegram/messages', TelegramMessageViewSet, basename='telegram-message')
router.register(r'telegram/associations', AccountGroupAssociationViewSet, basename='account-group-association')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
]
