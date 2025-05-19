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
        self.red_company_user1 = User.objects.create_user(username="1@redcompany.com", email="1@redcompany.com", password="1234567890")
        self.red_company_user2 = User.objects.create_user(username="2@redcompany.com", email="2@redcompany.com", password="1234567890")
        self.green_company_user1 = User.objects.create_user(username="1@greencompany.com", email="1@greencompany.com", password="1234567890")
        self.green_company_user2 = User.objects.create_user(username="2@greencompany.com", email="2@greencompany.com", password="1234567890")

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

    def test_list_companies_unauthenticated(self):
        self.client.credentials()
        url = reverse("company-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_list_companies_authenticated(self):
        url = reverse("company-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertIn(response.data[0]["name"], ["Red company BV", "Green company BV"])
        
    def test_create_company_unauthenticated(self):
        self.client.credentials()
        url = reverse("company-list")
        data = {
            "name": "New Company",
            "vat_number": "VATNEW",
            "business_registration_number": "NL987654"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Company.objects.filter(name="New Company").exists())
        
    def test_create_company_authenticated(self):
        url = reverse("company-list")
        data = {
            "name": "New Company",
            "vat_number": "VATNEW",
            "business_registration_number": "NL987654"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Company.objects.count(), 3)
        self.assertEqual(Company.objects.get(id=response.data["id"]).name, "New Company")
        self.assertTrue(Company.objects.filter(name="New Company").exists())
        self.assertTrue(CompanyMembership.objects.filter(user=self.red_company_user1, company__name="New Company").exists())
        
    def test_create_company_with_existing_vat_number(self):
        url = reverse("company-list")
        data = {
            "name": "New Company",
            "vat_number": "VATRED",  # Existing VAT number
            "business_registration_number": "NL987654"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("vat_number", response.data["errors"][0]["attr"])
        self.assertFalse(CompanyMembership.objects.filter(user=self.red_company_user1, company__name="New Company").exists())
        
    def test_create_company_with_existing_business_registration_number(self):
        url = reverse("company-list")
        data = {
            "name": "New Company",
            "vat_number": "VATNEW",
            "business_registration_number": "NL123456"  # Existing business registration number
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("business_registration_number", response.data["errors"][0]["attr"])
        self.assertFalse(CompanyMembership.objects.filter(user=self.red_company_user1, company__name="New Company").exists())
        
    def test_put_company_unauthenticated(self):
        self.client.credentials()
        url = reverse("company-detail", args=[self.red_company.id])
        data = {
            "name": "Updated Company",
            "vat_number": "VATUPDATED",
            "business_registration_number": "NL111111"
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_put_company_authenticated_authorized(self):
        url = reverse("company-detail", args=[self.red_company.id])
        data = {
            "name": "Updated Company",
            "vat_number": "VATUPDATED",
            "business_registration_number": "NL111111"
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.red_company.refresh_from_db()
        self.assertEqual(self.red_company.name, "Updated Company")
    
    def test_put_company_authenticated_unauthorized(self):
        url = reverse("company-detail", args=[self.green_company.id])
        data = {
            "name": "Updated Company",
            "vat_number": "VATUPDATED",
            "business_registration_number": "NL111111"
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_put_company_with_existing_vat_number(self):
        url = reverse("company-detail", args=[self.red_company.id])
        data = {
            "name": "Updated Company",
            "vat_number": "VATGREEN",  # Existing VAT number
            "business_registration_number": "NL111111"
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("vat_number", response.data["errors"][0]["attr"])
        
    def test_put_company_with_existing_business_registration_number(self):
        url = reverse("company-detail", args=[self.red_company.id])
        data = {
            "name": "Updated Company",
            "vat_number": "VATUPDATED",
            "business_registration_number": "NL654321"  # Existing business registration number
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("business_registration_number", response.data["errors"][0]["attr"])
        
    def test_patch_company_unauthenticated(self):
        self.client.credentials()
        url = reverse("company-detail", args=[self.red_company.id])
        data = {
            "name": "Partially Updated Company"
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_company_authenticated_authorized(self):
        url = reverse("company-detail", args=[self.red_company.id])
        data = {
            "name": "Partially Updated Company"
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.red_company.refresh_from_db()
        self.assertEqual(self.red_company.name, "Partially Updated Company")

    def test_patch_company_authenticated_unauthorized(self):
        url = reverse("company-detail", args=[self.green_company.id])
        data = {
            "name": "Partially Updated Company"
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_company_with_existing_vat_number(self):
        url = reverse("company-detail", args=[self.red_company.id])
        data = {
            "vat_number": "VATGREEN"  # Existing VAT number
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("vat_number", response.data["errors"][0]["attr"])

    def test_patch_company_with_existing_business_registration_number(self):
        url = reverse("company-detail", args=[self.red_company.id])
        data = {
            "business_registration_number": "NL654321"  # Existing business registration number
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("business_registration_number", response.data["errors"][0]["attr"])

    def test_delete_company_unauthenticated(self):
        self.client.credentials()
        url = reverse("company-detail", args=[self.red_company.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_company_authenticated_authorized(self):
        url = reverse("company-detail", args=[self.red_company.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Company.objects.count(), 1)
        self.assertFalse(Company.objects.filter(id=self.red_company.id).exists())

    def test_delete_company_authenticated_unauthorized(self):
        url = reverse("company-detail", args=[self.green_company.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Company.objects.count(), 2)
        self.assertTrue(Company.objects.filter(id=self.green_company.id).exists())

    def test_list_companies_my(self):
        CompanyMembership.objects.create(user=self.red_company_user1, company=self.green_company)

        self.blue_company = Company.objects.create(
            name="Blue company BV",
            vat_number="VATBLUE",
            business_registration_number="NL9876543"
        )

        url = reverse("companies-my-list")
        response = self.client.get(url)

        company_list = [company["name"] for company in response.data]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Red company BV", company_list)
        self.assertIn("Green company BV", company_list)
        self.assertNotIn("Blue company BV", company_list)