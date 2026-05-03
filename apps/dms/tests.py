from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
from apps.dms.models import DMSConfig, Heartbeat
from apps.dms.tasks import check_dms_inactivity

User = get_user_model()

class DMSTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='Password123!',
            first_name='Test',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)
        self.config_url = reverse('dms:config')
        self.heartbeat_url = reverse('dms:heartbeat')
        self.cancel_url = reverse('dms:cancel')

    def test_get_dms_config_creates_default(self):
        response = self.client.get(self.config_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['inactivity_threshold_days'], 90)
        self.assertEqual(response.data['cooling_off_days'], 7)
        self.assertEqual(response.data['status'], DMSConfig.Status.ACTIVE)

    def test_update_dms_config(self):
        data = {
            'inactivity_threshold_days': 120,
            'cooling_off_days': 14
        }
        response = self.client.patch(self.config_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['inactivity_threshold_days'], 120)
        self.assertEqual(response.data['cooling_off_days'], 14)

    def test_update_dms_config_invalid_threshold(self):
        data = {'inactivity_threshold_days': 5}
        response = self.client.patch(self.config_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_heartbeat(self):
        data = {'source': Heartbeat.Source.WEB}
        response = self.client.post(self.heartbeat_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Heartbeat.objects.count(), 1)
        self.assertEqual(Heartbeat.objects.first().user, self.user)
        
    def test_heartbeat_resets_dms_warning(self):
        dms_config, _ = DMSConfig.objects.get_or_create(user=self.user)
        dms_config.status = DMSConfig.Status.WARNING_1
        dms_config.save()
        
        data = {'source': Heartbeat.Source.MOBILE}
        self.client.post(self.heartbeat_url, data)
        
        dms_config.refresh_from_db()
        self.assertEqual(dms_config.status, DMSConfig.Status.ACTIVE)

    def test_cancel_dms_cooling_off(self):
        dms_config, _ = DMSConfig.objects.get_or_create(user=self.user)
        dms_config.status = DMSConfig.Status.COOLING_OFF
        dms_config.save()

        response = self.client.post(self.cancel_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        dms_config.refresh_from_db()
        self.assertEqual(dms_config.status, DMSConfig.Status.ACTIVE)

    def test_cancel_dms_not_triggered(self):
        dms_config, _ = DMSConfig.objects.get_or_create(user=self.user)
        dms_config.status = DMSConfig.Status.ACTIVE
        dms_config.save()

        response = self.client.post(self.cancel_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('apps.notifications.tasks.send_sms_notification.delay')
    @patch('apps.notifications.tasks.send_email_notification.delay')
    def test_dms_task_triggers_warning_1(self, mock_email, mock_sms):
        dms_config, _ = DMSConfig.objects.get_or_create(user=self.user)
        dms_config.inactivity_threshold_days = 100
        dms_config.save()
        
        # Set last active to 76 days ago (threshold is 75)
        self.user.last_active_at = timezone.now() - timedelta(days=76)
        self.user.save()

        check_dms_inactivity()
        
        dms_config.refresh_from_db()
        self.assertEqual(dms_config.status, DMSConfig.Status.WARNING_1)
        mock_email.assert_called_once()

    @patch('apps.notifications.tasks.send_sms_notification.delay')
    @patch('apps.notifications.tasks.send_email_notification.delay')
    def test_dms_task_triggers_cooling_off(self, mock_email, mock_sms):
        dms_config, _ = DMSConfig.objects.get_or_create(user=self.user)
        dms_config.inactivity_threshold_days = 90
        dms_config.save()
        
        # Set last active to 91 days ago
        self.user.last_active_at = timezone.now() - timedelta(days=91)
        self.user.save()

        check_dms_inactivity()
        
        dms_config.refresh_from_db()
        self.assertEqual(dms_config.status, DMSConfig.Status.COOLING_OFF)
        mock_email.assert_called_once()
