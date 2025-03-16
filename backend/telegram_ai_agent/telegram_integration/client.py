from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import (
    MessageMediaDocument,
    MessageMediaPhoto,
    DocumentAttributeAudio,
    PeerChannel, 
    PeerChat, 
    InputPeerChannel, 
    InputPeerChat
)
from django.conf import settings
import asyncio
import logging
from datetime import datetime
from .models import TelegramAccount, TelegramGroup, TelegramMessage, AccountGroupAssociation
from asgiref.sync import sync_to_async
from django.db import transaction
from functools import partial

logger = logging.getLogger(__name__)

class TelegramClientManager:
    """
    Class to manage Telegram client instances and handle authentication
    """
    def __init__(self, account):
        self.account = account
        self.client = None

    def process_unsupported_media(self, media):
        """Handle unsupported media types"""
        media_type = type(media).__name__
        return f"[Unsupported message type: {media_type}]"

    def process_voice_message(self, message):
        """Process voice messages"""
        duration = None
        if hasattr(message.media, 'document') and message.media.document.attributes:
            for attr in message.media.document.attributes:
                if isinstance(attr, DocumentAttributeAudio):
                    duration = attr.duration
        
        if duration:
            return f"[Voice message: {duration} seconds]"
        return "[Voice message]"

    def process_document(self, message):
        """Process document messages"""
        file_name = "unnamed_file"
        file_size = None
        
        if hasattr(message.media, 'document'):
            if message.media.document.attributes:
                for attr in message.media.document.attributes:
                    if hasattr(attr, 'file_name'):
                        file_name = attr.file_name
            file_size = message.media.document.size
            
        size_str = f" ({file_size} bytes)" if file_size else ""
        return f"[Document: {file_name}{size_str}]"

    def process_photo(self, message):
        """Process photo messages"""
        caption = message.message if message.message else ""
        return f"[Photo{': ' + caption if caption else ''}]"

    async def create_client(self):
        """Create and initialize a Telegram client for the account"""
        try:
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
        """Authenticate the client with Telegram"""
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
                    
            self.account.session_string = self.client.session.save()
            self.account.is_active = True
            self.account.save()
            
            return True
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False

    async def join_group(self, group_username_or_link):
        """Join a Telegram group"""
        try:
            if not self.client or not await self.client.is_user_authorized():
                logger.error("Client not authenticated")
                return None
                
            entity = await self.client.get_entity(group_username_or_link)
            
            if hasattr(entity, 'id') and hasattr(entity, 'title'):
                group, created = TelegramGroup.objects.update_or_create(
                    group_id=entity.id,
                    defaults={
                        'name': entity.title,
                        'username': getattr(entity, 'username', None),
                        'is_active': True
                    }
                )
                
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
        """Try different methods to get the correct entity"""
        try:
            if str(group_id).startswith('-100'):
                group_id = str(group_id)[4:]
            group_id = int(group_id)
            
            errors = []
            
            try:
                return await self.client.get_entity(InputPeerChannel(
                    channel_id=group_id,
                    access_hash=0
                ))
            except Exception as e:
                errors.append(f"Channel attempt: {str(e)}")
                
            try:
                return await self.client.get_entity(InputPeerChat(
                    chat_id=group_id
                ))
            except Exception as e:
                errors.append(f"Chat attempt: {str(e)}")
                
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
        """Collect messages from a Telegram group"""
        try:
            if not self.client or not await self.client.is_user_authorized():
                logger.error("Client not authenticated")
                return 0

            entity = await self.get_entity_by_id(group.group_id)
            
            if not entity:
                logger.error(f"Could not resolve entity for group ID: {group.group_id}")
                return 0
                
            logger.info(f"Successfully got entity of type {type(entity).__name__}: {entity.title}")
            
            @sync_to_async
            def message_exists(message_id):
                return TelegramMessage.objects.filter(
                    group=group,
                    message_id=message_id
                ).exists()

            @sync_to_async
            def create_message(msg_data):
                return TelegramMessage.objects.create(**msg_data)

            try:
                messages = await self.client.get_messages(
                    entity,
                    limit=limit
                )
                logger.info(f"Retrieved {len(messages)} messages from group")
            except Exception as e:
                logger.error(f"Error getting messages: {str(e)}")
                return 0

            count = 0
            for message in messages:
                try:
                    if not message.text and not message.media:
                        continue

                    exists = await message_exists(message.id)
                    if exists:
                        continue

                    sender_name = 'Unknown'
                    sender_id = None
                    sender_username = None
                    
                    if hasattr(message, 'sender_id') and message.sender_id:
                        sender_id = str(message.sender_id)
                        if hasattr(message, 'sender') and message.sender:
                            sender = message.sender
                            first_name = getattr(sender, 'first_name', '') or ''
                            last_name = getattr(sender, 'last_name', '') or ''
                            sender_name = f"{first_name} {last_name}".strip() or getattr(sender, 'username', 'Unknown')
                            sender_username = getattr(sender, 'username', None)
                        else:
                            sender_name = f"User{message.sender_id}"

                    message_text = message.text or ''
                    message_type = 'TEXT'

                    if message.media:
                        if isinstance(message.media, MessageMediaDocument) and hasattr(message.media.document, 'attributes'):
                            for attr in message.media.document.attributes:
                                if isinstance(attr, DocumentAttributeAudio) and attr.voice:
                                    message_type = 'VOICE'
                                    message_text = self.process_voice_message(message)
                                    break
                            if message_type == 'TEXT':  # If not voice, then it's a regular document
                                message_type = 'DOCUMENT'
                                message_text = self.process_document(message)
                        elif isinstance(message.media, MessageMediaPhoto):
                            message_type = 'PHOTO'
                            message_text = self.process_photo(message)
                        else:
                            message_type = 'OTHER'
                            message_text = self.process_unsupported_media(message.media)

                    msg_data = {
                        'group': group,
                        'message_id': message.id,
                        'sender_id': sender_id,
                        'sender_name': sender_name,
                        'sender_username': sender_username,
                        'text': message_text,
                        'message_type': message_type,
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
        """Sync historical messages from a Telegram group"""
        try:
            if not self.client or not await self.client.is_user_authorized():
                logger.error("Client not authenticated")
                return 0
            
            entity = await self.get_entity_by_id(group.group_id)
            
            if not entity:
                logger.error(f"Could not resolve entity for group ID: {group.group_id}")
                return 0
                
            logger.info(f"Successfully got entity: {entity.title}")

            @sync_to_async
            def message_exists(message_id):
                return TelegramMessage.objects.filter(
                    group=group,
                    message_id=message_id
                ).exists()

            @sync_to_async
            def get_message(message_id):
                try:
                    return TelegramMessage.objects.get(
                        group=group,
                        message_id=message_id
                    )
                except TelegramMessage.DoesNotExist:
                    return None

            @sync_to_async
            def update_message(message_obj):
                message_obj.save()

            @sync_to_async
            def create_message(msg_data):
                return TelegramMessage.objects.create(**msg_data)

            messages = await self.client.get_messages(
                entity,
                limit=limit,
                reverse=True
            )
            
            count = 0
            for message in messages:
                try:
                    if not message.text and not message.media:
                        continue

                    exists = await message_exists(message.id)
                    if exists:
                        message_obj = await get_message(message.id)
                        if message_obj and not message_obj.sender_username:
                            message_obj.sender_username = sender_username
                            await update_message(message_obj)
                        continue

                    sender_name = 'Unknown'
                    sender_id = None
                    sender_username = None
                    
                    if hasattr(message, 'sender_id') and message.sender_id:
                        sender_id = str(message.sender_id)
                        if hasattr(message, 'sender') and message.sender:
                            sender = message.sender
                            first_name = getattr(sender, 'first_name', '') or ''
                            last_name = getattr(sender, 'last_name', '') or ''
                            sender_name = f"{first_name} {last_name}".strip() or getattr(sender, 'username', 'Unknown')
                            sender_username = getattr(sender, 'username', None)
                        else:
                            sender_name = f"User{message.sender_id}"

                    message_text = message.text or ''
                    message_type = 'TEXT'

                    if message.media:
                        if isinstance(message.media, MessageMediaDocument) and hasattr(message.media.document, 'attributes'):
                            for attr in message.media.document.attributes:
                                if isinstance(attr, DocumentAttributeAudio) and attr.voice:
                                    message_type = 'VOICE'
                                    message_text = self.process_voice_message(message)
                                    break
                            if message_type == 'TEXT':  # If not voice, then it's a regular document
                                message_type = 'DOCUMENT'
                                message_text = self.process_document(message)
                        elif isinstance(message.media, MessageMediaPhoto):
                            message_type = 'PHOTO'
                            message_text = self.process_photo(message)
                        else:
                            message_type = 'OTHER'
                            message_text = self.process_unsupported_media(message.media)

                    msg_data = {
                        'group': group,
                        'message_id': message.id,
                        'sender_id': sender_id,
                        'sender_name': sender_name,
                        'sender_username': sender_username,
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

            logger.info(f"Successfully synced {count} messages from {group.name}")
            return count

        except Exception as e:
            logger.error(f"Error in sync_historical_messages: {str(e)}")
            return 0
            
    async def disconnect(self):
        """Disconnect the client"""
        if self.client:
            await self.client.disconnect()
