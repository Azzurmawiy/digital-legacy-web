from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.notifications.models import Notification
from apps.notifications.tasks import send_email_notification, send_sms_notification
from unittest.mock import patch

User = get_user_model()

class NotificationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='Password123!',
            first_name='Test',
            last_name='User',
            phone='+2348012345678'
        )
        self.client.force_authenticate(user=self.user)
        self.history_url = reverse('notifications:history')

    @patch('apps.notifications.tasks.send_mail')
    def test_send_email_task_success(self, mock_send_mail):
        mock_send_mail.return_value = 1
        
        send_email_notification(
            user_id=self.user.id,
            subject="Test Subject",
            message="Test Message"
        )
        
        notification = Notification.objects.filter(user=self.user, channel=Notification.Channel.EMAIL).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.status, Notification.Status.SENT)
        self.assertEqual(notification.subject, "Test Subject")
        mock_send_mail.assert_called_once()

    @patch('apps.notifications.tasks.send_mail')
    def test_send_email_task_failure(self, mock_send_mail):
        mock_send_mail.side_effect = Exception("SMTP Error")
        
        send_email_notification(
            user_id=self.user.id,
            subject="Test Subject",
            message="Test Message"
        )
        
        notification = Notification.objects.filter(user=self.user, channel=Notification.Channel.EMAIL).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.status, Notification.Status.FAILED)
        self.assertIn("SMTP Error", notification.error_message)

    def test_send_sms_task_success(self):
        # We don't have actual Twilio hooked up, so testing the mock implementation
        send_sms_notification(
            user_id=self.user.id,
            message="Test SMS"
        )
        
        notification = Notification.objects.filter(user=self.user, channel=Notification.Channel.SMS).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.status, Notification.Status.SENT)

    def test_send_sms_task_no_phone(self):
        user2 = User.objects.create_user(email='nophone@example.com', password='pw')
        send_sms_notification(
            user_id=user2.id,
            message="Test SMS"
        )
        
        notification = Notification.objects.filter(user=user2, channel=Notification.Channel.SMS).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.status, Notification.Status.FAILED)
        self.assertIn("No phone number", notification.error_message)

    def test_get_notification_history(self):
        Notification.objects.create(
            user=self.user,
            channel=Notification.Channel.EMAIL,
            subject="Test 1",
            message="Message 1",
            status=Notification.Status.SENT
        )
        Notification.objects.create(
            user=self.user,
            channel=Notification.Channel.SMS,
            message="Message 2",
            status=Notification.Status.FAILED
        )

        response = self.client.get(self.history_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['channel'], Notification.Channel.SMS) # Order by -created_at
