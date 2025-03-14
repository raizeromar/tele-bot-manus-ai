from telethon import TelegramClient, events
from telethon.sessions import StringSession
from django.conf import settings
import asyncio
import logging
from datetime import datetime
from .models import TelegramAccount, TelegramGroup, TelegramMessage, AccountGroupAssociation

logger = logging.getLogger(__name__)

class TelegramClientManager:
    """
    Class to manage Telegram client instances and handle authentication
    """
    def __init__(self, account):
        self.account = account
        self.client = None
        
    async def create_client(self):
        """Create and initialize a Telegram client for the account"""
        try:
            # Use StringSession for persistence
            if self.account.session_string:
                session = StringSession(self.account.session_string)
            else:
                session = StringSession()
                
            self.client = TelegramClient(
                session,
                api_id=self.account.api_id,
                api_hash=self.account.api_hash
            )
            
            await self.client.connect()
            return self.client
        except Exception as e:
            logger.error(f"Error creating Telegram client: {str(e)}")
            raise
            
    async def authenticate(self, phone_code_callback=None):
        """
        Authenticate the client with Telegram
        
        Args:
            phone_code_callback: Optional callback function to get phone code
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            if not self.client:
                await self.create_client()
                
            if not await self.client.is_user_authorized():
                await self.client.send_code_request(self.account.phone_number)
                
                if phone_code_callback:
                    phone_code = await phone_code_callback()
                    await self.client.sign_in(self.account.phone_number, phone_code)
                else:
                    logger.error("No phone code callback provided for authentication")
                    return False
                    
            # Save the session string for future use
            self.account.session_string = self.client.session.save()
            self.account.is_active = True
            self.account.save()
            
            return True
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
            
    async def join_group(self, group_username_or_link):
        """
        Join a Telegram group
        
        Args:
            group_username_or_link: Username or invite link of the group
            
        Returns:
            TelegramGroup: The joined group object or None if failed
        """
        try:
            if not self.client or not await self.client.is_user_authorized():
                logger.error("Client not authenticated")
                return None
                
            # Join the group
            entity = await self.client.get_entity(group_username_or_link)
            
            if hasattr(entity, 'id') and hasattr(entity, 'title'):
                # Create or update the group in the database
                group, created = TelegramGroup.objects.update_or_create(
                    group_id=entity.id,
                    defaults={
                        'name': entity.title,
                        'username': getattr(entity, 'username', None),
                        'is_active': True
                    }
                )
                
                # Create association between account and group
                AccountGroupAssociation.objects.update_or_create(
                    account=self.account,
                    group=group,
                    defaults={'is_active': True}
                )
                
                return group
            else:
                logger.error(f"Entity is not a group: {entity}")
                return None
        except Exception as e:
            logger.error(f"Error joining group: {str(e)}")
            return None
            
    async def collect_messages(self, group, limit=100):
        """
        Collect messages from a Telegram group
        
        Args:
            group: TelegramGroup object
            limit: Maximum number of messages to collect
            
        Returns:
            int: Number of new messages collected
        """
        try:
            if not self.client or not await self.client.is_user_authorized():
                logger.error("Client not authenticated")
                return 0
                
            # Get the group entity
            entity = await self.client.get_entity(group.group_id)
            
            # Get messages
            messages = await self.client.get_messages(entity, limit=limit)
            
            # Save messages to database
            count = 0
            for message in messages:
                if not message.text:
                    continue
                    
                # Check if message already exists
                exists = TelegramMessage.objects.filter(
                    group=group,
                    message_id=message.id
                ).exists()
                
                if not exists:
                    # Get sender info
                    if message.sender_id:
                        try:
                            sender = await self.client.get_entity(message.sender_id)
                            sender_name = getattr(sender, 'first_name', '') + ' ' + getattr(sender, 'last_name', '')
                            sender_name = sender_name.strip() or getattr(sender, 'username', 'Unknown')
                        except:
                            sender_name = 'Unknown'
                    else:
                        sender_name = 'Unknown'
                        
                    # Save message
                    TelegramMessage.objects.create(
                        group=group,
                        message_id=message.id,
                        sender_id=message.sender_id,
                        sender_name=sender_name,
                        text=message.text,
                        date=message.date,
                        is_processed=False
                    )
                    count += 1
            
            # Update last collection timestamp
            association = AccountGroupAssociation.objects.get(account=self.account, group=group)
            association.last_collection = datetime.now()
            association.save()
            
            return count
        except Exception as e:
            logger.error(f"Error collecting messages: {str(e)}")
            return 0
            
    async def disconnect(self):
        """Disconnect the client"""
        if self.client:
            await self.client.disconnect()
