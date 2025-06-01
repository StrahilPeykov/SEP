from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from core.models.company import Company
from core.models.company_membership import CompanyMembership
from core.tests.setup_functions import paint_companies_setup

User = get_user_model()


class CompanyUserManagementAPITests(APITestCase):
    def setUp(self):
        paint_companies_setup(self)

    def test_add_user_to_company_unauthenticated(self):
        self.client.credentials()
        url = reverse("company-users-list", args=[self.red_company.id])
        data = {
            "username": "1@greencompany.com"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_user_to_company_authenticated_authorized(self):
        url = reverse("company-users-list", args=[self.red_company.id])
        data = {
            "username": "1@greencompany.com"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            CompanyMembership.objects.filter(
                user=self.green_company_user1,
                company=self.red_company
            ).exists()
        )

    def test_add_user_to_company_authenticated_unauthorized(self):
        url = reverse("company-users-list", args=[self.green_company.id])
        data = {
            "username": "1@redcompany.com"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(
            CompanyMembership.objects.filter(
                user=self.red_company_user1,
                company=self.green_company
            ).exists()
        )

    def test_remove_user_from_company_unauthenticated(self):
        self.client.credentials()
        url = reverse("company-users-detail", args=[self.red_company.id, self.red_company_user1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(
            CompanyMembership.objects.filter(
                user=self.red_company_user1,
                company=self.red_company
            ).exists()
        )

    def test_remove_user_from_company_authenticated_authorized(self):
        url = reverse("company-users-detail", args=[self.red_company.id, self.red_company_user2.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            CompanyMembership.objects.filter(
                user=self.red_company_user2,
                company=self.red_company
            ).exists()
        )

    def test_remove_user_from_company_authenticated_unauthorized(self):
        url = reverse("company-users-detail", args=[self.green_company.id, self.green_company_user1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            CompanyMembership.objects.filter(
                user=self.green_company_user1,
                company=self.green_company
            ).exists()
        )

    def test_get_users_in_company_unauthenticated(self):
        self.client.credentials()
        url = reverse("company-users-list", args=[self.red_company.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_users_in_company_authenticated_authorized(self):
        url = reverse("company-users-list", args=[self.red_company.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_users_in_company_authenticated_unauthorized(self):
        url = reverse("company-users-list", args=[self.green_company.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
