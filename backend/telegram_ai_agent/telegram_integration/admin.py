from django.contrib import admin
from .models import TelegramAccount, TelegramGroup, TelegramMessage, AccountGroupAssociation

@admin.register(TelegramAccount)
class TelegramAccountAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'user', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('phone_number', 'user__username')
    readonly_fields = ('created_at', 'updated_at', 'last_code_request')

@admin.register(TelegramGroup)
class TelegramGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'group_id', 'username', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'username')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(TelegramMessage)
class TelegramMessageAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'group', 'sender_name', 'date', 'is_processed')
    list_filter = ('is_processed', 'date', 'created_at')
    search_fields = ('sender_name', 'text')
    readonly_fields = ('created_at',)

@admin.register(AccountGroupAssociation)
class AccountGroupAssociationAdmin(admin.ModelAdmin):
    list_display = ('account', 'group', 'is_active', 'joined_at')
    list_filter = ('is_active', 'joined_at')
    search_fields = ('account__phone_number', 'group__name')
    readonly_fields = ('joined_at', 'last_collection')

