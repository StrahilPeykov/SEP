from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from core.models import Company, CompanyMembership

User = get_user_model()

class CompanyAPITests(APITestCase):
    def setUp(self):
        # Create two users
        self.user1 = User.objects.create_user(username='alice', password='pass123')
        self.user2 = User.objects.create_user(username='bob',   password='pass123')

        # Obtain JWT for user1
        url = reverse('token_obtain_pair')
        resp = self.client.post(
            url,
            {
                'username': 'alice',
                'password': 'pass123'
            },
            format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.access_token = resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Create an existing company
        self.company = Company.objects.create(name='Acme Inc.')

    def test_list_companies(self):
        url = reverse('company-list')
        resp = self.client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Should see at least the one we created
        names = [c['name'] for c in resp.data]
        self.assertIn('Acme Inc.', names)

    def test_create_company(self):
        url = reverse('company-list')
        data = {'name': 'NewCo'}
        resp = self.client.post(url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Company.objects.filter(name='NewCo').exists())

    def test_retrieve_company(self):
        url = reverse('company-detail', args=[self.company.pk])
        resp = self.client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['name'], 'Acme Inc.')

    def test_update_company(self):
        url = reverse('company-detail', args=[self.company.pk])
        resp = self.client.patch(url, {'name': 'Acme Ltd.'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.company.refresh_from_db()
        self.assertEqual(self.company.name, 'Acme Ltd.')

    def test_delete_company(self):
        url = reverse('company-detail', args=[self.company.pk])
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Company.objects.filter(pk=self.company.pk).exists())

    def test_add_user_action(self):
        # initially bob is not a member
        self.assertFalse(CompanyMembership.objects.filter(user=self.user2, company=self.company).exists())

        url = reverse('company-add-user', args=[self.company.pk])
        resp = self.client.post(url, {'user_id': self.user2.pk}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(CompanyMembership.objects.filter(user=self.user2, company=self.company).exists())

    def test_unauthenticated_cannot_access(self):
        self.client.credentials()  # remove auth
        url = reverse('company-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
