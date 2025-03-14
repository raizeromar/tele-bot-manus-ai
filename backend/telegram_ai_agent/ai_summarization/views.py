from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
import asyncio
import logging

from .models import Summary, SummaryFeedback
from .serializers import SummarySerializer, SummaryFeedbackSerializer
from .summarizer import GeminiSummarizer
from telegram_integration.models import TelegramGroup, TelegramMessage

logger = logging.getLogger(__name__)

class SummaryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing summaries"""
    serializer_class = SummarySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Return summaries for groups associated with the user's accounts
        from telegram_integration.models import TelegramAccount, AccountGroupAssociation
        
        user_accounts = TelegramAccount.objects.filter(user=self.request.user)
        group_ids = AccountGroupAssociation.objects.filter(
            account__in=user_accounts
        ).values_list('group_id', flat=True)
        
        return Summary.objects.filter(group_id__in=group_ids)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Endpoint to manually generate a summary for a specific group and time period
        """
        group_id = request.data.get('group_id')
        days = int(request.data.get('days', 7))
        
        if not group_id:
            return Response({
                'error': 'Group ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the group
        try:
            from telegram_integration.models import TelegramAccount, AccountGroupAssociation
            
            # Check if the user has access to this group
            user_accounts = TelegramAccount.objects.filter(user=request.user)
            has_access = AccountGroupAssociation.objects.filter(
                account__in=user_accounts,
                group_id=group_id
            ).exists()
            
            if not has_access:
                return Response({
                    'error': 'You do not have access to this group'
                }, status=status.HTTP_403_FORBIDDEN)
            
            group = TelegramGroup.objects.get(id=group_id)
        except TelegramGroup.DoesNotExist:
            return Response({
                'error': 'Group not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Calculate time period
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Get messages for the period
        messages = TelegramMessage.objects.filter(
            group=group,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        if not messages:
            return Response({
                'error': 'No messages found for the specified period'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Format messages for summarization
        message_list = []
        for msg in messages:
            message_list.append({
                'sender_name': msg.sender_name,
                'date': msg.date,
                'text': msg.text
            })
        
        # Generate summary
        try:
            # Create summarizer
            summarizer = GeminiSummarizer()
            
            # Run in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Generate summary
            summary_text = loop.run_until_complete(
                summarizer.generate_summary(message_list, group.name, start_date, end_date)
            )
            
            loop.close()
            
            # Create summary object
            summary = Summary.objects.create(
                group=group,
                start_date=start_date,
                end_date=end_date,
                content=summary_text
            )
            
            # Mark messages as processed
            messages.update(is_processed=True)
            
            return Response({
                'message': 'Summary generated successfully',
                'summary': SummarySerializer(summary).data
            })
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return Response({
                'error': f'Error generating summary: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SummaryFeedbackViewSet(viewsets.ModelViewSet):
    """ViewSet for managing summary feedback"""
    serializer_class = SummaryFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SummaryFeedback.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        # Check if user already provided feedback for this summary
        summary_id = request.data.get('summary')
        
        if not summary_id:
            return Response({
                'error': 'Summary ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        existing_feedback = SummaryFeedback.objects.filter(
            summary_id=summary_id,
            user=request.user
        ).first()
        
        if existing_feedback:
            return Response({
                'error': 'You have already provided feedback for this summary',
                'feedback': SummaryFeedbackSerializer(existing_feedback).data
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return super().create(request, *args, **kwargs)
