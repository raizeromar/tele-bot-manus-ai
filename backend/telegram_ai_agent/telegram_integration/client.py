from telethon import TelegramClient, events
from telethon.sessions import StringSession
from django.conf import settings
import asyncio
import logging
from datetime import datetime
from .models import TelegramAccount, TelegramGroup, TelegramMessage, AccountGroupAssociation
from asgiref.sync import sync_to_async
from django.db import transaction
from telethon.tl.types import PeerChannel, PeerChat, InputPeerChannel, InputPeerChat
from functools import partial

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
            # Create a new session or load existing one
            session = StringSession(self.account.session_string) if self.account.session_string else StringSession()
            
            self.client = TelegramClient(
                session,
                api_id=self.account.api_id,
                api_hash=self.account.api_hash,
                device_model="Python",
                system_version="Windows",
                app_version="1.0",
                connection_retries=10,
                retry_delay=2,
                timeout=20,
                request_retries=5
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
            
    async def get_entity_by_id(self, group_id):
        """
        Try different methods to get the correct entity
        """
        try:
            # Try different peer types
            from telethon.tl.types import PeerChannel, PeerChat, InputPeerChannel, InputPeerChat
            
            # Remove any "-100" prefix if it exists
            if str(group_id).startswith('-100'):
                group_id = str(group_id)[4:]
            group_id = int(group_id)
            
            errors = []
            
            # Try as Channel first (most common for supergroups and channels)
            try:
                return await self.client.get_entity(InputPeerChannel(
                    channel_id=group_id,
                    access_hash=0  # We'll let Telegram figure out the access hash
                ))
            except Exception as e:
                errors.append(f"Channel attempt: {str(e)}")
                
            # Try as Chat (for regular groups)
            try:
                return await self.client.get_entity(InputPeerChat(
                    chat_id=group_id
                ))
            except Exception as e:
                errors.append(f"Chat attempt: {str(e)}")
                
            # Try with just the ID
            try:
                return await self.client.get_entity(group_id)
            except Exception as e:
                errors.append(f"Direct ID attempt: {str(e)}")
                
            logger.error(f"All entity resolution attempts failed: {errors}")
            return None
            
        except Exception as e:
            logger.error(f"Error in get_entity_by_id: {str(e)}")
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
            entity = await self.get_entity_by_id(group.group_id)
            
            if not entity:
                logger.error(f"Could not resolve entity for group ID: {group.group_id}")
                return 0
                
            logger.info(f"Successfully got entity of type {type(entity).__name__}: {entity.title}")
            
            # Async wrapper for database operations
            @sync_to_async
            def update_group(name, username):
                group.name = name
                group.username = username
                group.save()

            @sync_to_async
            def message_exists(message_id):
                return TelegramMessage.objects.filter(
                    group=group,
                    message_id=message_id
                ).exists()

            @sync_to_async
            def create_message(msg_data):
                return TelegramMessage.objects.create(**msg_data)

            # Get messages
            try:
                messages = await self.client.get_messages(
                    entity,
                    limit=limit
                )
                logger.info(f"Retrieved {len(messages)} messages from group")
            except Exception as e:
                logger.error(f"Error getting messages: {str(e)}")
                return 0

            # Process messages
            count = 0
            for message in messages:
                try:
                    # Skip empty messages
                    if not message.text and not message.media:
                        continue

                    # Check if message exists
                    if await message_exists(message.id):
                        continue

                    # Prepare message data
                    sender_name = 'Unknown'
                    sender_id = None
                    
                    if hasattr(message, 'sender_id') and message.sender_id:
                        sender_id = str(message.sender_id)
                        if hasattr(message, 'sender') and message.sender:
                            sender = message.sender
                            sender_name = (getattr(sender, 'first_name', '') + ' ' + 
                                         getattr(sender, 'last_name', '')).strip() or \
                                         getattr(sender, 'username', 'Unknown')
                        else:
                            sender_name = f"User{message.sender_id}"

                    # Handle message text and media
                    message_text = message.text or ''
                    if message.media:
                        media_type = type(message.media).__name__
                        if message_text:
                            message_text += f" [Media: {media_type}]"
                        else:
                            message_text = f"[Media: {media_type}]"

                    # Create message
                    msg_data = {
                        'group': group,
                        'message_id': message.id,
                        'sender_id': sender_id,
                        'sender_name': sender_name,
                        'text': message_text,
                        'date': message.date,
                        'is_processed': False
                    }
                    
                    await create_message(msg_data)
                    count += 1

                    if count % 50 == 0:
                        logger.info(f"Processed {count} new messages so far")

                except Exception as msg_e:
                    logger.error(f"Error processing message {message.id}: {str(msg_e)}")
                    continue

            logger.info(f"Successfully collected {count} new messages from {group.name}")
            return count

        except Exception as e:
            logger.error(f"Error in collect_messages: {str(e)}")
            return 0
            
    async def sync_historical_messages(self, group, limit=1000):
        """
        Sync historical messages from a Telegram group, including messages that existed
        before the account was added to the system.
        """
        try:
            if not self.client or not await self.client.is_user_authorized():
                logger.error("Client not authenticated")
                return 0
            
            logger.info(f"Starting sync for group: {group.name} (ID: {group.group_id})")
        
            try:
                # Convert group_id to integer if it's stored as string
                group_id = int(group.group_id)
                # Get the group entity
                entity = await self.client.get_entity(group_id)
                logger.info(f"Successfully got entity: {entity.title}")
            
            except ValueError as ve:
                logger.error(f"Invalid group ID format: {group.group_id}")
                return 0
            except Exception as e:
                logger.error(f"Error getting entity: {str(e)}")
                return 0

            try:
                # Get messages with more flexible parameters
                logger.info(f"Fetching messages from group {entity.title}")
                messages = await self.client.get_messages(
                    entity,
                    limit=limit,
                    reverse=True  # Start from oldest messages
                )
                logger.info(f"Found {len(messages)} messages")
            
            except Exception as e:
                logger.error(f"Error fetching messages: {str(e)}")
                return 0

            # Save messages to database
            count = 0
            for message in messages:
                try:
                    # Skip empty messages but process media messages
                    if not message.text and not message.media:
                        continue
                    
                    # Check if message already exists
                    exists = TelegramMessage.objects.filter(
                        group=group,
                        message_id=message.id
                    ).exists()
                
                    if not exists:
                        # Get sender info
                        sender_name = 'Unknown'
                        if message.sender_id:
                            try:
                                sender = await self.client.get_entity(message.sender_id)
                                sender_name = getattr(sender, 'first_name', '') + ' ' + getattr(sender, 'last_name', '')
                                sender_name = sender_name.strip() or getattr(sender, 'username', 'Unknown')
                            except Exception as e:
                                logger.warning(f"Could not get sender info: {str(e)}")
                    
                        # Handle message text
                        message_text = message.text or ''
                        if message.media:
                            media_type = type(message.media).__name__
                            if message_text:
                                message_text += f" [Media: {media_type}]"
                            else:
                                message_text = f"[Media: {media_type}]"
                    
                        # Save message
                        TelegramMessage.objects.create(
                            group=group,
                            message_id=message.id,
                            sender_id=str(message.sender_id) if message.sender_id else None,
                            sender_name=sender_name,
                            text=message_text,
                            date=message.date,
                            is_processed=False
                        )
                        count += 1
                    
                        if count % 100 == 0:
                            logger.info(f"Synced {count} messages so far from {group.name}")
                
                except Exception as msg_e:
                    logger.error(f"Error processing message {message.id}: {str(msg_e)}")
                    continue
        
            logger.info(f"Successfully synced {count} messages from {group.name}")
            return count
        
        except Exception as e:
            logger.error(f"Error in sync_historical_messages: {str(e)}")
            return 0
            
    async def disconnect(self):
        """Disconnect the client"""
        if self.client:
            await self.client.disconnect()
