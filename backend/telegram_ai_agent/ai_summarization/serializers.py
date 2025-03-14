from rest_framework import serializers
from .models import Summary, SummaryFeedback
from telegram_integration.serializers import TelegramGroupSerializer
from django.contrib.auth.models import User

class SummarySerializer(serializers.ModelSerializer):
    group = TelegramGroupSerializer(read_only=True)
    
    class Meta:
        model = Summary
        fields = ['id', 'group', 'start_date', 'end_date', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class SummaryFeedbackSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    
    class Meta:
        model = SummaryFeedback
        fields = ['id', 'summary', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
    
    def create(self, validated_data):
        # Set the user from the request
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
