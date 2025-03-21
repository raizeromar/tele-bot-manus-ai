from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from telethon.sessions import StringSession
from .models import TelegramAccount, TelegramGroup, TelegramMessage, AccountGroupAssociation
from .serializers import (
    TelegramAccountSerializer, 
    TelegramGroupSerializer, 
    TelegramMessageSerializer,
    AccountGroupAssociationSerializer,
    TelegramAuthenticateSerializer,
    TelegramVerifyCodeSerializer,
    TelegramAccountSyncSerializer,
    MessageCollectionSerializer
)
from .client import TelegramClientManager
import asyncio
import logging
from django.utils import timezone
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TelegramAccountViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Telegram accounts"""
    serializer_class = TelegramAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return TelegramAccount.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'], serializer_class=TelegramAuthenticateSerializer)
    def authenticate(self, request, pk=None):
        """
        Start authentication process for a Telegram account.
        """
        serializer = TelegramAuthenticateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        account = self.get_object()
        client_manager = TelegramClientManager(account)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            client = loop.run_until_complete(client_manager.create_client())
            
            # Force logout if there's an existing session
            if account.session_string:
                try:
                    loop.run_until_complete(client.log_out())
                    account.session_string = None
                    account.is_active = False
                    account.save()
                    
                    # Create a new client after logout
                    client = loop.run_until_complete(client_manager.create_client())
                except Exception as logout_error:
                    logger.warning(f"Logout error (non-critical): {str(logout_error)}")
            
            phone_number = serializer.validated_data.get('phone_number', account.phone_number)
            force_sms = serializer.validated_data.get('force_sms', False)
            
            # Send code request with force_sms
            result = loop.run_until_complete(client.send_code_request(
                phone=phone_number,
                force_sms=True  # Force SMS code
            ))
            
            # Store the session string immediately after code request
            session_string = client.session.save()
            account.session_string = session_string
            account.last_code_request = timezone.now()
            account.save()
            
            loop.run_until_complete(client_manager.disconnect())
            
            return Response({
                'message': 'Verification code sent to your phone',
                'request_id': str(account.id),
                'phone_code_hash': result.phone_code_hash,
                'timestamp': timezone.now().isoformat(),
                'expires_in': '5 minutes',
                'session_valid': bool(session_string),
                'force_sms': True  # Debug info
            })
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            error_message = str(e)
            if "PHONE_NUMBER_INVALID" in error_message:
                error_message = "Invalid phone number format. Please use international format (e.g., +1234567890)"
            elif "PHONE_NUMBER_BANNED" in error_message:
                error_message = "This phone number has been banned from Telegram. Please contact Telegram support."
            elif "PHONE_NUMBER_FLOOD" in error_message:
                error_message = "Too many code requests. Please wait before requesting another code."
            return Response({
                'error': error_message
            }, status=status.HTTP_400_BAD_REQUEST)
        finally:
            loop.close()

    @action(detail=True, methods=['post'], serializer_class=TelegramVerifyCodeSerializer)
    def verify_code(self, request, pk=None):
        """
        Verify the Telegram authentication code.
        """
        serializer = TelegramVerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        account = self.get_object()
        code = serializer.validated_data['code']
        phone_code_hash = serializer.validated_data['phone_code_hash']
        
        if not account.session_string:
            return Response({
                'error': 'No active session found. Please request a new code.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if code request is too old (5 minutes)
        if account.last_code_request:
            time_elapsed = timezone.now() - account.last_code_request
            if time_elapsed.total_seconds() > 300:  # 5 minutes
                return Response({
                    'error': 'Code has expired. Please request a new code.',
                    'elapsed_seconds': time_elapsed.total_seconds()
                }, status=status.HTTP_400_BAD_REQUEST)
        
        client_manager = TelegramClientManager(account)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Create client with existing session
            client = loop.run_until_complete(client_manager.create_client())
            
            try:
                # Sign in with the code
                result = loop.run_until_complete(client.sign_in(
                    phone=account.phone_number,
                    code=code,
                    phone_code_hash=phone_code_hash
                ))
                
                # Save the new session after successful sign in
                new_session_string = client.session.save()
                account.session_string = new_session_string
                account.is_active = True
                account.save()
                
                loop.run_until_complete(client_manager.disconnect())
                
                return Response({
                    'message': 'Authentication successful',
                    'account': TelegramAccountSerializer(account).data,
                    'session_valid': bool(new_session_string)  # Debug info
                })
                
            except Exception as sign_in_error:
                error_message = str(sign_in_error)
                if "PHONE_CODE_INVALID" in error_message:
                    error_message = "Invalid verification code. Please try again."
                elif "PHONE_CODE_EXPIRED" in error_message:
                    error_message = "Code has expired. Please request a new code using the authenticate endpoint."
                raise Exception(error_message)
            
        except Exception as e:
            logger.error(f"Verification error: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        finally:
            loop.close()

    @action(detail=True, 
            methods=['post'], 
            url_path='sync', 
            url_name='sync',
            serializer_class=TelegramAccountSyncSerializer)
    def sync_account(self, request, pk=None):
        """
        Sync all Telegram groups, channels, and chats from this account.
        """
        try:
            account = self.get_object()
            
            # Create client manager
            client_manager = TelegramClientManager(account)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Connect and authenticate client
                client = loop.run_until_complete(client_manager.create_client())
                
                if not loop.run_until_complete(client.is_user_authorized()):
                    return Response({
                        'error': 'Account not authenticated'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Get all dialogs (groups, channels, chats)
                dialogs = loop.run_until_complete(client.get_dialogs())
                
                groups_added = 0
                
                for dialog in dialogs:
                    entity = dialog.entity
                    
                    if dialog.is_group or dialog.is_channel:
                        # Create or update the group/channel
                        group, created = TelegramGroup.objects.update_or_create(
                            group_id=str(entity.id),
                            defaults={
                                'name': entity.title,
                                'username': getattr(entity, 'username', None),
                                'is_active': True
                            }
                        )
                        
                        # Create or update association
                        AccountGroupAssociation.objects.get_or_create(
                            account=account,
                            group=group,
                            defaults={'is_active': True}
                        )
                        
                        if created:
                            groups_added += 1
                
                return Response({
                    'status': 'success',
                    'message': f'Successfully synced account.',
                    'details': {
                        'groups_added': groups_added,
                        'total_chats': len(dialogs)
                    }
                })
                
            finally:
                # Always disconnect client and close loop
                loop.run_until_complete(client_manager.disconnect())
                loop.close()
                
        except Exception as e:
            logger.error(f"Account sync error: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class TelegramGroupViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Telegram groups"""
    serializer_class = TelegramGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Return groups associated with the user's accounts
        user_accounts = TelegramAccount.objects.filter(user=self.request.user)
        group_ids = AccountGroupAssociation.objects.filter(
            account__in=user_accounts
        ).values_list('group_id', flat=True)
        return TelegramGroup.objects.filter(id__in=group_ids)
    
    @action(detail=False, methods=['post'])
    def join(self, request):
        """
        Endpoint to join a Telegram group using a specified account
        """
        account_id = request.data.get('account_id')
        group_link = request.data.get('group_link')
        
        if not account_id or not group_link:
            return Response({
                'error': 'Account ID and group link are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the account
        try:
            account = TelegramAccount.objects.get(id=account_id, user=request.user)
        except TelegramAccount.DoesNotExist:
            return Response({
                'error': 'Account not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Create a client manager
        client_manager = TelegramClientManager(account)
        
        # Join the group asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Connect and authenticate the client
            client = loop.run_until_complete(client_manager.create_client())
            
            if not loop.run_until_complete(client.is_user_authorized()):
                return Response({
                    'error': 'Account not authenticated'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Join the group
            group = loop.run_until_complete(client_manager.join_group(group_link))
            
            if not group:
                return Response({
                    'error': 'Failed to join group'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Disconnect the client
            loop.run_until_complete(client_manager.disconnect())
            
            return Response({
                'message': 'Successfully joined group',
                'group': TelegramGroupSerializer(group).data
            })
        except Exception as e:
            logger.error(f"Join group error: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        finally:
            loop.close()
    
    @action(detail=True, 
            methods=['post'],
            serializer_class=MessageCollectionSerializer)
    def collect_messages(self, request, pk=None):
        """
        Collect messages from a Telegram group based on specified criteria
        """
        group = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        account_id = validated_data['account_id']
        collection_type = validated_data['collection_type']
        limit = validated_data.get('limit', 1000)
        
        try:
            account = TelegramAccount.objects.get(id=account_id, user=request.user)
        except TelegramAccount.DoesNotExist:
            return Response({
                'error': 'Account not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check association
        association = get_object_or_404(
            AccountGroupAssociation,
            account=account,
            group=group
        )
        
        # Setup client
        client_manager = TelegramClientManager(account)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Create and connect client
            client = loop.run_until_complete(client_manager.create_client())
            
            if not loop.run_until_complete(client.is_user_authorized()):
                return Response({
                    'error': 'Account not authenticated'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Collect messages
            count = loop.run_until_complete(client_manager.collect_messages(group, limit=limit))
            
            # Update last collection timestamp
            association.last_collection = timezone.now()
            association.save()
            
            return Response({
                'message': f'Successfully collected {count} messages',
                'collection_type': collection_type,
                'count': count
            })
            
        except Exception as e:
            logger.error(f"Message collection error: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        finally:
            # Cleanup
            try:
                loop.run_until_complete(client_manager.disconnect())
            except Exception as e:
                logger.error(f"Error disconnecting client: {str(e)}")
            loop.close()

    @action(detail=False, methods=['post'], url_path='sync-groups', url_name='sync_groups')
    def sync_groups(self, request):
        """
        Sync all Telegram groups that the user is already a member of.
        
        Expected payload:
        {
            "account_id": "integer - ID of your Telegram account"
        }
        """
        account_id = request.data.get('account_id')
        
        if not account_id:
            return Response({
                'error': 'Account ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            account = TelegramAccount.objects.get(id=account_id, user=request.user)
        except TelegramAccount.DoesNotExist:
            return Response({
                'error': 'Account not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        client_manager = TelegramClientManager(account)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Connect and authenticate the client
            client = loop.run_until_complete(client_manager.create_client())
            
            if not loop.run_until_complete(client.is_user_authorized()):
                return Response({
                    'error': 'Account not authenticated'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get all dialogs (chats and groups)
            dialogs = loop.run_until_complete(client.get_dialogs())
            
            # Filter for groups only
            groups_added = 0
            for dialog in dialogs:
                if dialog.is_group or dialog.is_channel:
                    group, created = TelegramGroup.objects.update_or_create(
                        group_id=str(dialog.entity.id),  # Convert to string to ensure compatibility
                        defaults={
                            'name': dialog.entity.title,
                            'username': getattr(dialog.entity, 'username', None),
                            'is_active': True
                        }
                    )
                    
                    # Create association if it doesn't exist
                    association, assoc_created = AccountGroupAssociation.objects.get_or_create(
                        account=account,
                        group=group,
                        defaults={'is_active': True}
                    )
                    
                    if created:
                        groups_added += 1
            
            # Disconnect the client
            loop.run_until_complete(client_manager.disconnect())
            
            return Response({
                'message': f'Successfully synced groups. Added {groups_added} new groups.',
                'groups_added': groups_added,
                'total_groups': len(dialogs)
            })
            
        except Exception as e:
            logger.error(f"Sync groups error: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        finally:
            loop.close()

    @action(detail=True, 
            methods=['post'],
            url_path='sync-messages',
            url_name='sync_messages',
            serializer_class=MessageCollectionSerializer)
    def sync_messages(self, request, pk=None):
        """
        Sync historical messages from a Telegram group
        """
        group = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        account_id = validated_data['account_id']
        limit = validated_data.get('limit', 1000)
        
        try:
            account = TelegramAccount.objects.get(id=account_id, user=request.user)
        except TelegramAccount.DoesNotExist:
            return Response({
                'error': 'Account not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check association
        try:
            association = AccountGroupAssociation.objects.get(
                account=account,
                group=group
            )
        except AccountGroupAssociation.DoesNotExist:
            return Response({
                'error': 'No association found between this account and group'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Setup client
        client_manager = TelegramClientManager(account)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Create and connect client
            client = loop.run_until_complete(client_manager.create_client())
            
            if not loop.run_until_complete(client.is_user_authorized()):
                return Response({
                    'error': 'Account not authenticated'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"Starting message sync for group {group.name} using account {account.phone_number}")
            
            # Sync historical messages
            count = loop.run_until_complete(
                client_manager.sync_historical_messages(group, limit=limit)
            )
            
            if count == 0:
                return Response({
                    'warning': 'No new messages were synced. This could mean either all messages are already synced or there was an issue accessing the group.',
                    'group_id': group.group_id,
                    'group_name': group.name
                }, status=status.HTTP_200_OK)
            
            # Update last collection timestamp
            association.last_collection = timezone.now()
            association.save()
            
            return Response({
                'message': f'Successfully synced {count} historical messages',
                'count': count,
                'group_name': group.name,
                'group_id': group.group_id
            })
            
        except Exception as e:
            logger.error(f"Message sync error: {str(e)}")
            return Response({
                'error': str(e),
                'group_id': group.group_id,
                'group_name': group.name
            }, status=status.HTTP_400_BAD_REQUEST)
        finally:
            try:
                loop.run_until_complete(client_manager.disconnect())
            except Exception as e:
                logger.error(f"Error disconnecting client: {str(e)}")
            loop.close()

class TelegramMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing Telegram messages"""
    serializer_class = TelegramMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Return messages from groups associated with the user's accounts
        user_accounts = TelegramAccount.objects.filter(user=self.request.user)
        group_ids = AccountGroupAssociation.objects.filter(
            account__in=user_accounts
        ).values_list('group_id', flat=True)
        return TelegramMessage.objects.filter(group_id__in=group_ids).order_by('-date')
    
    def list(self, request):
        # Filter by group if provided
        group_id = request.query_params.get('group_id')
        queryset = self.get_queryset()
        
        if group_id:
            queryset = queryset.filter(group_id=group_id)
        
        # Paginate the results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class AccountGroupAssociationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing account-group associations"""
    serializer_class = AccountGroupAssociationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AccountGroupAssociation.objects.filter(
            account__user=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """
        Endpoint to toggle the active status of an association
        """
        association = self.get_object()
        association.is_active = not association.is_active
        association.save()
        
        return Response({
            'message': f'Association is now {"active" if association.is_active else "inactive"}',
            'association': AccountGroupAssociationSerializer(association).data
        })
