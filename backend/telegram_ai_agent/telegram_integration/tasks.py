from celery import shared_task
import asyncio
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from .models import TelegramAccount, TelegramGroup, AccountGroupAssociation
from .client import TelegramClientManager

logger = logging.getLogger(__name__)

@shared_task
def collect_messages_from_all_groups():
    """
    Celery task to collect messages from all active groups for all active accounts
    This task is scheduled to run periodically
    """
    logger.info("Starting scheduled message collection task")
    
    # Get all active account-group associations
    associations = AccountGroupAssociation.objects.filter(
        is_active=True,
        account__is_active=True,
        group__is_active=True
    )
    
    collection_count = 0
    
    for association in associations:
        try:
            # Create a new event loop for each association
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Create client manager
            client_manager = TelegramClientManager(association.account)
            
            # Connect and authenticate
            client = loop.run_until_complete(client_manager.create_client())
            
            if not loop.run_until_complete(client.is_user_authorized()):
                logger.warning(f"Account {association.account.phone_number} not authenticated, skipping")
                continue
            
            # Collect messages
            count = loop.run_until_complete(
                client_manager.collect_messages(association.group, limit=200)
            )
            
            # Disconnect
            loop.run_until_complete(client_manager.disconnect())
            
            collection_count += count
            
            logger.info(f"Collected {count} new messages from {association.group.name} using account {association.account.phone_number}")
            
            # Update last collection timestamp
            association.last_collection = timezone.now()
            association.save()
            
            # Close the loop
            loop.close()
            
        except Exception as e:
            logger.error(f"Error collecting messages for association {association.id}: {str(e)}")
    
    logger.info(f"Completed scheduled message collection task. Total new messages: {collection_count}")
    return collection_count

@shared_task
def check_inactive_associations():
    """
    Celery task to check for inactive associations
    If an association hasn't collected messages in a week, mark it as inactive
    """
    logger.info("Checking for inactive associations")
    
    # Get associations that haven't collected messages in a week
    one_week_ago = timezone.now() - timedelta(days=7)
    
    associations = AccountGroupAssociation.objects.filter(
        is_active=True,
        last_collection__lt=one_week_ago
    )
    
    for association in associations:
        association.is_active = False
        association.save()
        logger.info(f"Marked association {association.id} as inactive due to inactivity")
    
    return len(associations)
