"""
Signal handlers for telegram_integration app
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TelegramMessage

@receiver(post_save, sender=TelegramMessage)
def handle_new_message(sender, instance, created, **kwargs):
    """
    Signal handler for new messages
    This can be used to trigger actions when new messages are saved
    """
    if created:
        # This is where you could add logic to be executed when a new message is created
        # For example, you might want to notify users or trigger immediate processing
        pass
