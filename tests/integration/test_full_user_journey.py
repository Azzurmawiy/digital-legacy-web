"""
tests/integration/test_full_user_journey.py

Sprint 8 — End-to-End Integration Tests
Tests the complete Digital Legacy App workflow from registration to asset release.
All tests use the Django test client and test database — no external services required.
"""
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.dms.models import DMSConfig, Heartbeat
from apps.beneficiary.models import Beneficiary
from apps.notifications.models import Notification

User = get_user_model()


class FullUserJourneyTest(APITestCase):
    """
    Integration test: Complete lifecycle from user creation through DMS release.
    Verifies that all components work together correctly end-to-end.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email='auwal@digitallegacy.test',
            password='SecurePassword123!',
            first_name='Auwal',
            last_name='Usman',
            phone='+2348012345678'
        )
        self.client.force_authenticate(user=self.user)

    # ──────────────────────────────────────────────────────
    # PART 1: DMS Configuration Journey
    # ──────────────────────────────────────────────────────

    def test_01_dms_config_created_on_first_access(self):
        """GET /dms/config/ creates a default config if none exists."""
        response = self.client.get(reverse('dms:config'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], DMSConfig.Status.ACTIVE)
        self.assertEqual(response.data['inactivity_threshold_days'], 90)
        self.assertTrue(DMSConfig.objects.filter(user=self.user).exists())

    def test_02_user_can_customise_dms_thresholds(self):
        """PATCH /dms/config/ saves custom threshold values."""
        response = self.client.patch(reverse('dms:config'), {
            'inactivity_threshold_days': 60,
            'cooling_off_days': 14,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['inactivity_threshold_days'], 60)
        self.assertEqual(response.data['cooling_off_days'], 14)

    def test_03_heartbeat_resets_warning_status(self):
        """POST /dms/heartbeat/ resets any WARNING status back to ACTIVE."""
        config, _ = DMSConfig.objects.get_or_create(user=self.user)
        config.status = DMSConfig.Status.WARNING_2
        config.save()

        response = self.client.post(reverse('dms:heartbeat'), {'source': 'WEB'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        config.refresh_from_db()
        self.assertEqual(config.status, DMSConfig.Status.ACTIVE)

    def test_04_cancel_cooling_off_returns_to_active(self):
        """POST /dms/cancel/ cancels cooling-off and resets to ACTIVE."""
        config, _ = DMSConfig.objects.get_or_create(user=self.user)
        config.status = DMSConfig.Status.COOLING_OFF
        config.save()

        response = self.client.post(reverse('dms:cancel'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        config.refresh_from_db()
        self.assertEqual(config.status, DMSConfig.Status.ACTIVE)

    # ──────────────────────────────────────────────────────
    # PART 2: Beneficiary Management Journey
    # ──────────────────────────────────────────────────────

    def test_05_add_beneficiary(self):
        """POST /beneficiaries/ creates a new beneficiary."""
        response = self.client.post(reverse('beneficiary:beneficiary-list'), {
            'name': 'Sarah Usman',
            'email': 'sarah@example.com',
            'relationship': 'Spouse',
            'permissions': {'can_view_vault': True},
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Beneficiary.objects.filter(user=self.user).count(), 1)

    def test_06_cannot_add_self_as_beneficiary(self):
        """Adding self email as beneficiary returns 400."""
        response = self.client.post(reverse('beneficiary:beneficiary-list'), {
            'name': 'Me',
            'email': self.user.email,
            'relationship': 'Self',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_07_list_only_own_beneficiaries(self):
        """GET /beneficiaries/ returns only the authenticated user's beneficiaries."""
        Beneficiary.objects.create(user=self.user, name='A', email='a@x.com', relationship='Friend')
        other = User.objects.create_user(email='other@test.com', password='pw12345678!')
        Beneficiary.objects.create(user=other, name='B', email='b@x.com', relationship='Friend')

        response = self.client.get(reverse('beneficiary:beneficiary-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)

    def test_08_delete_beneficiary(self):
        """DELETE /beneficiaries/<id>/ removes a beneficiary."""
        ben = Beneficiary.objects.create(user=self.user, name='A', email='a@x.com', relationship='Friend')
        response = self.client.delete(reverse('beneficiary:beneficiary-detail', args=[ben.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Beneficiary.objects.filter(id=ben.id).exists())

    # ──────────────────────────────────────────────────────
    # PART 3: Notification History Journey
    # ──────────────────────────────────────────────────────

    def test_09_notification_history_is_empty_initially(self):
        """GET /notifications/history/ returns empty list for a new user."""
        response = self.client.get(reverse('notifications:history'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_10_notification_history_shows_sent_notifications(self):
        """Sent notifications appear in the history endpoint."""
        Notification.objects.create(
            user=self.user,
            channel=Notification.Channel.EMAIL,
            subject='Test Warning',
            message='Inactive for 67 days.',
            status=Notification.Status.SENT,
        )
        response = self.client.get(reverse('notifications:history'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['subject'], 'Test Warning')

    # ──────────────────────────────────────────────────────
    # PART 4: Full DMS State Machine Journey
    # ──────────────────────────────────────────────────────

    @patch('apps.notifications.tasks.send_sms_notification.delay')
    @patch('apps.notifications.tasks.send_email_notification.delay')
    def test_11_full_dms_state_machine(self, mock_email, mock_sms):
        """
        Full DMS lifecycle: ACTIVE → WARNING_1 → WARNING_2 → COOLING_OFF → RELEASED
        """
        from apps.dms.tasks import check_dms_inactivity

        config, _ = DMSConfig.objects.get_or_create(user=self.user)
        config.inactivity_threshold_days = 100
        config.cooling_off_days = 1
        config.save()

        # 1) At 76 days inactive → should trigger WARNING_1
        self.user.last_active_at = timezone.now() - timedelta(days=76)
        self.user.save()
        check_dms_inactivity()
        config.refresh_from_db()
        self.assertEqual(config.status, DMSConfig.Status.WARNING_1)
        self.assertEqual(mock_email.call_count, 1)

        # 2) At 91 days inactive → should escalate to WARNING_2
        self.user.last_active_at = timezone.now() - timedelta(days=91)
        self.user.save()
        check_dms_inactivity()
        config.refresh_from_db()
        self.assertEqual(config.status, DMSConfig.Status.WARNING_2)
        self.assertEqual(mock_email.call_count, 2)

        # 3) At 101 days inactive → should trigger COOLING_OFF
        self.user.last_active_at = timezone.now() - timedelta(days=101)
        self.user.save()
        check_dms_inactivity()
        config.refresh_from_db()
        self.assertEqual(config.status, DMSConfig.Status.COOLING_OFF)
        self.assertEqual(mock_sms.call_count, 2)  # SMS sent at warning_2 and cooling off

        # 4) Simulate cooling off period expired → RELEASED
        config.last_triggered = timezone.now() - timedelta(days=2)
        config.save()

        with patch('apps.dms.release.release_assets_to_beneficiaries.delay') as mock_release:
            check_dms_inactivity()
            config.refresh_from_db()
            self.assertEqual(config.status, DMSConfig.Status.RELEASED)
            mock_release.assert_called_once_with(self.user.id)

    # ──────────────────────────────────────────────────────
    # PART 5: Asset Release Journey
    # ──────────────────────────────────────────────────────

    @patch('django.core.mail.send_mail')
    @patch('apps.notifications.tasks.send_email_notification.delay')
    def test_12_asset_release_notifies_all_beneficiaries(self, mock_email_task, mock_send_mail):
        """release_assets_to_beneficiaries emails each beneficiary and logs audit records."""
        from apps.dms.release import release_assets_to_beneficiaries

        Beneficiary.objects.create(user=self.user, name='Sarah', email='sarah@x.com', relationship='Spouse',
                                   permissions={'can_view_vault': True})
        Beneficiary.objects.create(user=self.user, name='John Jr.', email='john@x.com', relationship='Son',
                                   permissions={'can_view_vault': False})

        release_assets_to_beneficiaries(self.user.id)

        # One email sent to each beneficiary via send_mail + 1 confirmation via task
        self.assertEqual(mock_send_mail.call_count, 2)
        mock_email_task.assert_called_once()

        # Two audit Notification records created (one per beneficiary)
        audit_logs = Notification.objects.filter(user=self.user)
        self.assertEqual(audit_logs.count(), 2)

    @patch('apps.notifications.tasks.send_email_notification.delay')
    def test_13_asset_release_with_no_beneficiaries(self, mock_email_task):
        """release_assets_to_beneficiaries handles case with no beneficiaries gracefully."""
        from apps.dms.release import release_assets_to_beneficiaries

        release_assets_to_beneficiaries(self.user.id)

        # Should still send the owner a warning notification
        mock_email_task.assert_called_once()
        call_args = mock_email_task.call_args[0]
        self.assertIn('No Beneficiaries', call_args[1])
