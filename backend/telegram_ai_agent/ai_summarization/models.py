from django.db import models
from telegram_integration.models import TelegramGroup, TelegramMessage
from django.contrib.auth.models import User

class Summary(models.Model):
    """Model to store summaries of collected messages"""
    group = models.ForeignKey(TelegramGroup, on_delete=models.CASCADE, related_name='summaries')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-end_date']
        verbose_name_plural = 'Summaries'
    
    def __str__(self):
        return f"Summary for {self.group.name} ({self.start_date.date()} to {self.end_date.date()})"

class SummaryFeedback(models.Model):
    """Model to store user feedback on summaries"""
    summary = models.ForeignKey(Summary, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='summary_feedback')
    rating = models.IntegerField(choices=[(1, '1 - Poor'), (2, '2 - Fair'), (3, '3 - Good'), (4, '4 - Very Good'), (5, '5 - Excellent')])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('summary', 'user')
    
    def __str__(self):
        return f"Feedback by {self.user.username} on {self.summary}"
