from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from core.models.company import Company
from core.models.company_membership import CompanyMembership

User = get_user_model()


class UserProfileAPITests(APITestCase):
    def setUp(self):
        # Create a users
        self.user1 = User.objects.create_user(username="1@company.com", email="1@company.com",
                                                            password="1234567890")
        self.user2 = User.objects.create_user(username="2@company.com", email="2@company.com",
                                                            password="1234567890")

        # Obtain JWT for user1
        url = reverse("token_obtain_pair")
        resp = self.client.post(
            url, {"username": "1@company.com", "password": "1234567890"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.access_token = resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        # Create an existing company
        self.company = Company.objects.create(
            name="Company BV",
            vat_number="VAT",
            business_registration_number="NL123456"
        )

        CompanyMembership.objects.create(user=self.user1, company=self.company)
        CompanyMembership.objects.create(user=self.user2, company=self.company)

    def test_delete_current_user_authenticated(self):
        url = reverse("user_profile")

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user1.id).exists())
        #Assert that other users were not deleted
        self.assertTrue(User.objects.filter(id=self.user2.id).exists())

    def test_delete_current_user_unauthorized(self):
        self.client.credentials()
        url = reverse("user_profile")

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(User.objects.filter(id=self.user1.id).exists())

    def test_switch_user_and_delete_current_user_authenticated_authorized(self):
        self.user3 = User.objects.create_user(username="3@company.com", email="3@company.com",
                                              password="1234567890")
        url = reverse("token_obtain_pair")
        resp = self.client.post(
            url, {"username": "3@company.com", "password": "1234567890"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.access_token = resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        url = reverse("user_profile")

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user3.id).exists())
        # Assert that other users were not deleted
        self.assertTrue(User.objects.filter(id=self.user2.id).exists())
        self.assertTrue(User.objects.filter(id=self.user1.id).exists())
        
    def test_delete_current_user_and_check_company_membership(self):
        self.assertTrue(
            CompanyMembership.objects.filter(
                user=self.user1,
                company=self.company
            ).exists()
        )

        url = reverse("user_profile")

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(
            CompanyMembership.objects.filter(
                user=self.user1,
                company=self.company
            ).exists()
        )
        self.assertTrue(
            CompanyMembership.objects.filter(
                user=self.user2,
                company=self.company
            ).exists()
        )