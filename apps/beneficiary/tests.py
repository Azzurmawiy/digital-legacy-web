from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.beneficiary.models import Beneficiary

User = get_user_model()

class BeneficiaryTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='Password123!',
            first_name='Test',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)
        self.list_url = reverse('beneficiary:beneficiary-list')

    def test_create_beneficiary(self):
        data = {
            'name': 'John Doe',
            'email': 'johndoe@example.com',
            'relationship': 'Brother',
            'permissions': {'can_view_vault': True}
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Beneficiary.objects.count(), 1)
        self.assertEqual(Beneficiary.objects.first().user, self.user)
        self.assertEqual(response.data['permissions']['can_view_vault'], True)

    def test_cannot_add_self_as_beneficiary(self):
        data = {
            'name': 'Self',
            'email': self.user.email,
            'relationship': 'Self'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['error']['message'])

    def test_cannot_add_duplicate_beneficiary(self):
        Beneficiary.objects.create(
            user=self.user,
            name='Jane Doe',
            email='jane@example.com',
            relationship='Sister'
        )
        data = {
            'name': 'Jane Doe Duplicate',
            'email': 'jane@example.com',
            'relationship': 'Cousin'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['error']['message'])

    def test_list_beneficiaries(self):
        Beneficiary.objects.create(
            user=self.user, name='Ben 1', email='ben1@example.com', relationship='Friend'
        )
        Beneficiary.objects.create(
            user=self.user, name='Ben 2', email='ben2@example.com', relationship='Friend'
        )
        
        # Another user's beneficiary
        other_user = User.objects.create_user(email='other@example.com', password='pw')
        Beneficiary.objects.create(
            user=other_user, name='Ben 3', email='ben3@example.com', relationship='Friend'
        )

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only return the 2 beneficiaries owned by the authenticated user
        # Note: Pagination wraps it in 'results'
        self.assertEqual(len(response.data['data']), 2)

    def test_update_beneficiary(self):
        ben = Beneficiary.objects.create(
            user=self.user, name='Ben 1', email='ben1@example.com', relationship='Friend',
            permissions={"can_view_vault": False}
        )
        url = reverse('beneficiary:beneficiary-detail', args=[ben.id])
        data = {
            'name': 'Ben Updated',
            'email': 'ben1@example.com',
            'relationship': 'Friend',
            'permissions': {"can_view_vault": True}
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Ben Updated')
        self.assertTrue(response.data['permissions']['can_view_vault'])

    def test_delete_beneficiary(self):
        ben = Beneficiary.objects.create(
            user=self.user, name='Ben 1', email='ben1@example.com', relationship='Friend'
        )
        url = reverse('beneficiary:beneficiary-detail', args=[ben.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Beneficiary.objects.count(), 0)
