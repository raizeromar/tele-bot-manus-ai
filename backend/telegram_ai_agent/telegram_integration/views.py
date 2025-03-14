from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import TelegramAccount, TelegramGroup, TelegramMessage, AccountGroupAssociation
from .serializers import (
    TelegramAccountSerializer, 
    TelegramGroupSerializer, 
    TelegramMessageSerializer,
    AccountGroupAssociationSerializer
)
from .client import TelegramClientManager
import asyncio
import logging

logger = logging.getLogger(__name__)

class TelegramAccountViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Telegram accounts"""
    serializer_class = TelegramAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return TelegramAccount.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def authenticate(self, request, pk=None):
        """
        Endpoint to initiate authentication for a Telegram account
        Returns a request_id that should be used when submitting the verification code
        """
        account = self.get_object()
        
        # Create a client manager
        client_manager = TelegramClientManager(account)
        
        # Start authentication process asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Connect the client
            client = loop.run_until_complete(client_manager.create_client())
            
            # Send code request
            loop.run_until_complete(client.send_code_request(account.phone_number))
            
            # Generate a unique request ID for this authentication session
            # In a real implementation, you would store this in a cache or database
            # For simplicity, we'll just use the account ID
            request_id = str(account.id)
            
            # Disconnect the client
            loop.run_until_complete(client_manager.disconnect())
            
            return Response({
                'message': 'Verification code sent to your phone',
                'request_id': request_id
            })
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        finally:
            loop.close()
    
    @action(detail=True, methods=['post'])
    def verify_code(self, request, pk=None):
        """
        Endpoint to verify the code received on the Telegram account
        """
        account = self.get_object()
        code = request.data.get('code')
        request_id = request.data.get('request_id')
        
        if not code:
            return Response({
                'error': 'Verification code is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not request_id or request_id != str(account.id):
            return Response({
                'error': 'Invalid request ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create a client manager
        client_manager = TelegramClientManager(account)
        
        # Verify the code asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Connect the client
            client = loop.run_until_complete(client_manager.create_client())
            
            # Sign in with the code
            loop.run_until_complete(client.sign_in(account.phone_number, code))
            
            # Save the session string
            account.session_string = client.session.save()
            account.is_active = True
            account.save()
            
            # Disconnect the client
            loop.run_until_complete(client_manager.disconnect())
            
            return Response({
                'message': 'Authentication successful',
                'account': TelegramAccountSerializer(account).data
            })
        except Exception as e:
            logger.error(f"Verification error: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        finally:
            loop.close()

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
    
    @action(detail=True, methods=['post'])
    def collect_messages(self, request, pk=None):
        """
        Endpoint to manually collect messages from a group
        """
        group = self.get_object()
        account_id = request.data.get('account_id')
        limit = int(request.data.get('limit', 100))
        
        if not account_id:
            return Response({
                'error': 'Account ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the account
        try:
            account = TelegramAccount.objects.get(id=account_id, user=request.user)
        except TelegramAccount.DoesNotExist:
            return Response({
                'error': 'Account not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the account is associated with the group
        try:
            association = AccountGroupAssociation.objects.get(account=account, group=group)
        except AccountGroupAssociation.DoesNotExist:
            return Response({
                'error': 'Account is not associated with this group'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create a client manager
        client_manager = TelegramClientManager(account)
        
        # Collect messages asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Connect and authenticate the client
            client = loop.run_until_complete(client_manager.create_client())
            
            if not loop.run_until_complete(client.is_user_authorized()):
                return Response({
                    'error': 'Account not authenticated'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Collect messages
            count = loop.run_until_complete(client_manager.collect_messages(group, limit))
            
            # Disconnect the client
            loop.run_until_complete(client_manager.disconnect())
            
            return Response({
                'message': f'Successfully collected {count} new messages',
                'count': count
            })
        except Exception as e:
            logger.error(f"Collect messages error: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        finally:
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
