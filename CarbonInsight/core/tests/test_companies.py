from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from core.models.company import Company
from core.models.company_membership import CompanyMembership

User = get_user_model()


class CompanyAPITests(APITestCase):
    def setUp(self):
        # Create two users
        self.user1 = User.objects.create_user(username="alice@example.com", email="alice@example.com", password="pass123")
        self.user2 = User.objects.create_user(username="bob@example.com", email="bob@example.com", password="pass123")

        # Obtain JWT for user1
        url = reverse("token_obtain_pair")
        resp = self.client.post(
            url, {"username": "alice@example.com", "password": "pass123"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.access_token = resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        # Create an existing company
        self.company = Company.objects.create(
            name="Test company BV",
            vat_number="VAT123456",
            business_registration_number="NL123456"
        )
        # Add user1 to the company
        CompanyMembership.objects.create(user=self.user1, company=self.company)

    def test_list_companies(self):
        url = reverse("company-list")
        resp = self.client.get(url, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Should see at least the one we created
        names = [c["name"] for c in resp.data]
        self.assertIn("Test company BV", names)

    def test_create_company(self):
        url = reverse("company-list")
        data = {
            "name": "NewCo",
            "vat_number": "VAT654321",
            "business_registration_number": "NL654321"
        }
        resp = self.client.post(url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Company.objects.filter(name="NewCo").exists())

    def test_retrieve_company(self):
        url = reverse("company-detail", args=[self.company.pk])
        resp = self.client.get(url, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["name"], "Test company BV")
        self.assertEqual(resp.data["vat_number"], "VAT123456")
        self.assertEqual(resp.data["business_registration_number"], "NL123456")

    def test_update_company(self):
        url = reverse("company-detail", args=[self.company.pk])
        resp = self.client.patch(url, {"name": "Test company Inc"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.company.refresh_from_db()
        self.assertEqual(self.company.name, "Test company Inc")
        self.assertEqual(self.company.vat_number, "VAT123456")
        self.assertEqual(self.company.business_registration_number, "NL123456")

    def test_delete_company(self):
        url = reverse("company-detail", args=[self.company.pk])
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Company.objects.filter(pk=self.company.pk).exists())

    def test_add_user_action(self):
        # initially bob is not a member
        self.assertFalse(
            CompanyMembership.objects.filter(
                user=self.user2, company=self.company
            ).exists()
        )

        url = reverse("company-add-user", args=[self.company.pk])
        resp = self.client.post(url, {"username": self.user2.username}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(
            CompanyMembership.objects.filter(
                user=self.user2, company=self.company
            ).exists()
        )

    def test_add_user_action_invalid_user(self):
        url = reverse("company-add-user", args=[self.company.pk])
        resp = self.client.post(url, {"username": "invalid_username"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_user_action_no_permission(self):
        # Create a new user and company
        self.user3 = User.objects.create_user(username="charlie", password="pass123")
        self.company2 = Company.objects.create(
            name="Another company",
            vat_number="VAT654321",
            business_registration_number="NL654321"
        )

        # Try to add user3 to company2 without permission
        url = reverse("company-add-user", args=[self.company2.pk])
        resp = self.client.post(url, {"username": self.user3.username}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_remove_user_action(self):
        # First, add user2 to the company
        CompanyMembership.objects.create(user=self.user2, company=self.company)

        # Check that user2 is now a member
        self.assertTrue(
            CompanyMembership.objects.filter(
                user=self.user2, company=self.company
            ).exists()
        )

        url = reverse("company-remove-user", args=[self.company.pk])
        resp = self.client.post(url, {"username": self.user2.username}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertFalse(
            CompanyMembership.objects.filter(
                user=self.user2, company=self.company
            ).exists()
        )

    def test_remove_user_action_invalid_user(self):
        url = reverse("company-remove-user", args=[self.company.pk])
        resp = self.client.post(url, {"username": "invalid_username"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_remove_user_action_no_permission(self):
        # Create a new user and company
        self.user3 = User.objects.create_user(username="charlie", password="pass123")
        self.company2 = Company.objects.create(
            name="Another company",
            vat_number="VAT654321",
            business_registration_number="NL654321"
        )

        # Try to remove user3 from company2 without permission
        url = reverse("company-remove-user", args=[self.company2.pk])
        resp = self.client.post(url, {"username": self.user3.username}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access(self):
        self.client.credentials()  # remove auth
        url = reverse("company-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
