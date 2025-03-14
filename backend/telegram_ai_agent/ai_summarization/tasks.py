from celery import shared_task
import asyncio
import logging
from django.utils import timezone
from datetime import timedelta

from .models import Summary
from .summarizer import GeminiSummarizer
from telegram_integration.models import TelegramGroup, TelegramMessage, AccountGroupAssociation

logger = logging.getLogger(__name__)

@shared_task
def generate_weekly_summaries():
    """
    Celery task to generate weekly summaries for all active groups
    This task is scheduled to run once a week
    """
    logger.info("Starting weekly summary generation task")
    
    # Get all active groups that have associations with active accounts
    active_group_ids = AccountGroupAssociation.objects.filter(
        is_active=True,
        account__is_active=True
    ).values_list('group_id', flat=True).distinct()
    
    active_groups = TelegramGroup.objects.filter(
        id__in=active_group_ids,
        is_active=True
    )
    
    # Calculate time period for the past week
    end_date = timezone.now()
    start_date = end_date - timedelta(days=7)
    
    summary_count = 0
    
    for group in active_groups:
        try:
            # Get messages for the period that haven't been processed
            messages = TelegramMessage.objects.filter(
                group=group,
                date__gte=start_date,
                date__lte=end_date,
                is_processed=False
            ).order_by('date')
            
            if not messages:
                logger.info(f"No new messages to summarize for group {group.name}")
                continue
            
            # Format messages for summarization
            message_list = []
            for msg in messages:
                message_list.append({
                    'sender_name': msg.sender_name,
                    'date': msg.date,
                    'text': msg.text
                })
            
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
            Summary.objects.create(
                group=group,
                start_date=start_date,
                end_date=end_date,
                content=summary_text
            )
            
            # Mark messages as processed
            messages.update(is_processed=True)
            
            summary_count += 1
            logger.info(f"Successfully generated summary for group {group.name}")
            
        except Exception as e:
            logger.error(f"Error generating summary for group {group.name}: {str(e)}")
    
    logger.info(f"Completed weekly summary generation task. Total summaries: {summary_count}")
    return summary_count

@shared_task
def cleanup_old_summaries():
    """
    Celery task to clean up old summaries
    This task is scheduled to run monthly
    """
    logger.info("Starting old summaries cleanup task")
    
    # Delete summaries older than 6 months
    six_months_ago = timezone.now() - timedelta(days=180)
    
    deleted_count = Summary.objects.filter(
        created_at__lt=six_months_ago
    ).delete()[0]
    
    logger.info(f"Completed old summaries cleanup task. Deleted {deleted_count} summaries")
    return deleted_count
