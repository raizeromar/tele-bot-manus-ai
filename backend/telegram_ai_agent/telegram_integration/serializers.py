from rest_framework import serializers
from .models import TelegramAccount, TelegramGroup, TelegramMessage, AccountGroupAssociation
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id']

class TelegramAccountSyncSerializer(serializers.Serializer):
    """
    Serializer for the sync account endpoint.
    """
    phone_number = serializers.CharField(required=True)
    api_id = serializers.CharField(required=True)

    def validate(self, data):
        """
        Check that the account exists and belongs to the user
        """
        try:
            account = TelegramAccount.objects.get(
                phone_number=data['phone_number'],
                api_id=data['api_id'],
                user=self.context['request'].user
            )
        except TelegramAccount.DoesNotExist:
            raise serializers.ValidationError("Account not found with provided phone number and API ID")
        return data

class TelegramAccountSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    sync_url = serializers.HyperlinkedIdentityField(
        view_name='telegram-account-sync',
        lookup_url_kwarg='pk',
        read_only=True
    )
    
    class Meta:
        model = TelegramAccount
        fields = ['id', 'user', 'phone_number', 'api_id', 'api_hash', 'is_active', 
                 'created_at', 'updated_at', 'sync_url']
        read_only_fields = ['id', 'user', 'is_active', 'created_at', 'updated_at']
        extra_kwargs = {
            'api_hash': {'write_only': True}
        }
    
    def create(self, validated_data):
        user = self.context['request'].user
        return TelegramAccount.objects.create(user=user, **validated_data)

class TelegramGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramGroup
        fields = ['id', 'name', 'group_id', 'username', 'is_active']
        read_only_fields = ['id']

class TelegramMessageSerializer(serializers.ModelSerializer):
    group = TelegramGroupSerializer(read_only=True)
    
    class Meta:
        model = TelegramMessage
        fields = ['id', 'group', 'message_id', 'sender_id', 'sender_name', 'text', 'date', 'is_processed', 'created_at']
        read_only_fields = ['id', 'created_at']

class AccountGroupAssociationSerializer(serializers.ModelSerializer):
    account = TelegramAccountSerializer(read_only=True)
    group = TelegramGroupSerializer(read_only=True)
    
    class Meta:
        model = AccountGroupAssociation
        fields = ['id', 'account', 'group', 'is_active', 'joined_at', 'last_collection']
        read_only_fields = ['id', 'joined_at', 'last_collection']

class TelegramAuthenticateSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=False, help_text="Optional: Override the stored phone number")
    force_sms = serializers.BooleanField(required=False, default=False, help_text="Force SMS code instead of Telegram app")

class TelegramVerifyCodeSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, help_text="The verification code received from Telegram")
    phone_code_hash = serializers.CharField(required=True, help_text="The phone_code_hash received from the authenticate endpoint")
