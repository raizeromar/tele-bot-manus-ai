import unittest
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from telegram_integration.models import TelegramAccount, TelegramGroup, TelegramMessage, AccountGroupAssociation
from ai_summarization.models import Summary, SummaryFeedback

class TelegramIntegrationTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create test account
        self.account = TelegramAccount.objects.create(
            user=self.user,
            phone_number='+1234567890',
            api_id='12345',
            api_hash='abcdef1234567890',
            is_active=True
        )
        
        # Create test group
        self.group = TelegramGroup.objects.create(
            name='Test Group',
            group_id=123456789,
            username='test_group',
            is_active=True
        )
        
        # Create association
        self.association = AccountGroupAssociation.objects.create(
            account=self.account,
            group=self.group,
            is_active=True
        )
        
        # Create test messages
        self.message1 = TelegramMessage.objects.create(
            group=self.group,
            message_id=1,
            sender_id=987654321,
            sender_name='Test User 1',
            text='This is a test message 1',
            date=timezone.now() - timedelta(days=1),
            is_processed=False
        )
        
        self.message2 = TelegramMessage.objects.create(
            group=self.group,
            message_id=2,
            sender_id=987654322,
            sender_name='Test User 2',
            text='This is a test message 2',
            date=timezone.now() - timedelta(hours=12),
            is_processed=False
        )
    
    def test_account_creation(self):
        """Test that account was created correctly"""
        self.assertEqual(TelegramAccount.objects.count(), 1)
        self.assertEqual(self.account.phone_number, '+1234567890')
        self.assertEqual(self.account.user, self.user)
        self.assertTrue(self.account.is_active)
    
    def test_group_creation(self):
        """Test that group was created correctly"""
        self.assertEqual(TelegramGroup.objects.count(), 1)
        self.assertEqual(self.group.name, 'Test Group')
        self.assertEqual(self.group.username, 'test_group')
    
    def test_association_creation(self):
        """Test that association was created correctly"""
        self.assertEqual(AccountGroupAssociation.objects.count(), 1)
        self.assertEqual(self.association.account, self.account)
        self.assertEqual(self.association.group, self.group)
    
    def test_message_creation(self):
        """Test that messages were created correctly"""
        self.assertEqual(TelegramMessage.objects.count(), 2)
        self.assertEqual(self.message1.sender_name, 'Test User 1')
        self.assertEqual(self.message2.sender_name, 'Test User 2')
    
    def test_message_filtering(self):
        """Test filtering messages by group"""
        messages = TelegramMessage.objects.filter(group=self.group)
        self.assertEqual(messages.count(), 2)
        
        # Test filtering by processed status
        unprocessed = TelegramMessage.objects.filter(is_processed=False)
        self.assertEqual(unprocessed.count(), 2)
        
        # Mark one as processed
        self.message1.is_processed = True
        self.message1.save()
        
        unprocessed = TelegramMessage.objects.filter(is_processed=False)
        self.assertEqual(unprocessed.count(), 1)

class AISummarizationTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create test group
        self.group = TelegramGroup.objects.create(
            name='Test Group',
            group_id=123456789,
            username='test_group',
            is_active=True
        )
        
        # Create test summary
        self.start_date = timezone.now() - timedelta(days=7)
        self.end_date = timezone.now()
        
        self.summary = Summary.objects.create(
            group=self.group,
            start_date=self.start_date,
            end_date=self.end_date,
            content='This is a test summary of the group discussions.'
        )
        
        # Create test feedback
        self.feedback = SummaryFeedback.objects.create(
            summary=self.summary,
            user=self.user,
            rating=4,
            comment='Good summary!'
        )
    
    def test_summary_creation(self):
        """Test that summary was created correctly"""
        self.assertEqual(Summary.objects.count(), 1)
        self.assertEqual(self.summary.group, self.group)
        self.assertEqual(self.summary.content, 'This is a test summary of the group discussions.')
    
    def test_feedback_creation(self):
        """Test that feedback was created correctly"""
        self.assertEqual(SummaryFeedback.objects.count(), 1)
        self.assertEqual(self.feedback.summary, self.summary)
        self.assertEqual(self.feedback.user, self.user)
        self.assertEqual(self.feedback.rating, 4)
        self.assertEqual(self.feedback.comment, 'Good summary!')
    
    def test_summary_filtering(self):
        """Test filtering summaries by group"""
        summaries = Summary.objects.filter(group=self.group)
        self.assertEqual(summaries.count(), 1)
        
        # Test ordering
        summaries = Summary.objects.all().order_by('-end_date')
        self.assertEqual(summaries.first(), self.summary)

if __name__ == '__main__':
    unittest.main()
