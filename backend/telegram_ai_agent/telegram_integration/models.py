from django.db import models
from django.contrib.auth.models import User

class TelegramAccount(models.Model):
    """Model to store Telegram account credentials and session information"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='telegram_accounts')
    phone_number = models.CharField(max_length=20)
    api_id = models.CharField(max_length=20)
    api_hash = models.CharField(max_length=64)
    session_string = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.phone_number} ({self.user.username})"

class TelegramGroup(models.Model):
    """Model to store information about Telegram groups being monitored"""
    name = models.CharField(max_length=255)
    group_id = models.BigIntegerField()
    username = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class TelegramMessage(models.Model):
    """Model to store messages collected from Telegram groups"""
    group = models.ForeignKey(TelegramGroup, on_delete=models.CASCADE, related_name='messages')
    message_id = models.BigIntegerField()
    sender_id = models.BigIntegerField(null=True, blank=True)
    sender_name = models.CharField(max_length=255, null=True, blank=True)
    text = models.TextField()
    date = models.DateTimeField()
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.message_id} from {self.sender_name}"

class AccountGroupAssociation(models.Model):
    """Model to track which accounts are monitoring which groups"""
    account = models.ForeignKey(TelegramAccount, on_delete=models.CASCADE, related_name='group_associations')
    group = models.ForeignKey(TelegramGroup, on_delete=models.CASCADE, related_name='account_associations')
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_collection = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('account', 'group')

    def __str__(self):
        return f"{self.account.phone_number} - {self.group.name}"
