from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from core.models.company import Company
from core.models.company_membership import CompanyMembership

User = get_user_model()


class CompanyUserManagementAPITests(APITestCase):
    def setUp(self):
        # Create two users
        self.red_company_user1 = User.objects.create_user(username="1@redcompany.com", email="1@redcompany.com",
                                                          password="1234567890")
        self.red_company_user2 = User.objects.create_user(username="2@redcompany.com", email="2@redcompany.com",
                                                          password="1234567890")
        self.green_company_user1 = User.objects.create_user(username="1@greencompany.com", email="1@greencompany.com",
                                                            password="1234567890")
        self.green_company_user2 = User.objects.create_user(username="2@greencompany.com", email="2@greencompany.com",
                                                            password="1234567890")

        # Obtain JWT for user1
        url = reverse("token_obtain_pair")
        resp = self.client.post(
            url, {"username": "1@redcompany.com", "password": "1234567890"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.access_token = resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        # Create an existing company
        self.red_company = Company.objects.create(
            name="Red company BV",
            vat_number="VATRED",
            business_registration_number="NL123456"
        )
        self.green_company = Company.objects.create(
            name="Green company BV",
            vat_number="VATGREEN",
            business_registration_number="NL654321"
        )

        # Add users to companies
        CompanyMembership.objects.create(user=self.red_company_user1, company=self.red_company)
        CompanyMembership.objects.create(user=self.red_company_user2, company=self.red_company)
        CompanyMembership.objects.create(user=self.green_company_user1, company=self.green_company)
        CompanyMembership.objects.create(user=self.green_company_user2, company=self.green_company)

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
