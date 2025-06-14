"""
Tests for companies API
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from core.models.company import Company
from core.models.company_membership import CompanyMembership
from core.tests.setup_functions import paint_companies_setup

User = get_user_model()


class CompanyAPITests(APITestCase):
    def setUp(self):
        paint_companies_setup(self)
        self.blue_company.delete()

    def test_list_companies_unauthenticated(self):
        """
        Test for getting a list of companies when not logged in.
        """

        self.client.credentials()
        url = reverse("company-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_list_companies_authenticated(self):
        """
        Test for getting list of companies.
        """

        url = reverse("company-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertIn(response.data[0]["name"], ["Red company BV", "Green company BV"])
        
    def test_create_company_unauthenticated(self):
        """
        Test for creating a company without logging in.
        """
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
        """
        Test for creating a company when logged in.
        """

        current_company_count = Company.objects.count()
        url = reverse("company-list")
        data = {
            "name": "New Company",
            "vat_number": "VATNEW",
            "business_registration_number": "NL987654"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Company.objects.count(), current_company_count+1)
        self.assertEqual(Company.objects.get(id=response.data["id"]).name, "New Company")
        self.assertTrue(Company.objects.filter(name="New Company").exists())
        self.assertTrue(CompanyMembership.objects.filter(user=self.red_company_user1, company__name="New Company").exists())
        
    def test_create_company_with_existing_vat_number(self):
        """
        Test for creating a company with existing vat number.
        """

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
        """
        Test for creating a company with existing business registration number.
        """

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
        """
        Test for editing a company with a put request without logging in.
        """

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
        """
        Test for editing a company that the user is authorized to operate with a put request.
        """

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
        """
        Test for editing a company that the user is not authorized to operate with a put request.
        """

        url = reverse("company-detail", args=[self.green_company.id])
        data = {
            "name": "Updated Company",
            "vat_number": "VATUPDATED",
            "business_registration_number": "NL111111"
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_put_company_with_existing_vat_number(self):
        """
        Test for editing a company and giving it an already existing vat number with a put request.
        """

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
        """
        Test for editing a company and giving it an existing business registration number with a put request.
        """

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
        """
        Test for editing a company with a patch request without logging in.
        """

        self.client.credentials()
        url = reverse("company-detail", args=[self.red_company.id])
        data = {
            "name": "Partially Updated Company"
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_company_authenticated_authorized(self):
        """
        Test for editing a company that the user is authorized to operate with a patch request.
        """

        url = reverse("company-detail", args=[self.red_company.id])
        data = {
            "name": "Partially Updated Company"
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.red_company.refresh_from_db()
        self.assertEqual(self.red_company.name, "Partially Updated Company")

    def test_patch_company_authenticated_unauthorized(self):
        """
        Test for editing a company that the user is not authorized to operate with a patch request.
        """

        url = reverse("company-detail", args=[self.green_company.id])
        data = {
            "name": "Partially Updated Company"
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_company_with_existing_vat_number(self):
        """
        Test for editing a company and giving it an existing vat number with a patch request.
        """

        url = reverse("company-detail", args=[self.red_company.id])
        data = {
            "vat_number": "VATGREEN"  # Existing VAT number
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("vat_number", response.data["errors"][0]["attr"])

    def test_patch_company_with_existing_business_registration_number(self):
        """
        Test for editing a company and giving it an existing business registration number with a patch request.
        """

        url = reverse("company-detail", args=[self.red_company.id])
        data = {
            "business_registration_number": "NL654321"  # Existing business registration number
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("business_registration_number", response.data["errors"][0]["attr"])

    def test_delete_company_unauthenticated(self):
        """
        Test for deleting a company with a delete request without logging in.
        """

        self.client.credentials()
        url = reverse("company-detail", args=[self.red_company.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_company_authenticated_authorized(self):
        """
        Test for deleting a company that the user is authorized to operate with a delete request.
        """

        company_count = Company.objects.count()
        url = reverse("company-detail", args=[self.red_company.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Company.objects.count(), company_count-1)
        self.assertFalse(Company.objects.filter(id=self.red_company.id).exists())

    def test_delete_company_authenticated_unauthorized(self):
        """
        Test for deleting a company that the user is not authorized to operate with a delete request.
        """

        company_count = Company.objects.count()
        url = reverse("company-detail", args=[self.green_company.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Company.objects.count(), company_count)
        self.assertTrue(Company.objects.filter(id=self.green_company.id).exists())

    def test_list_companies_my(self):
        """
        Test for a logged in user to get the list of the companies they are authorized to operate.
        """

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

    def test_create_company_authenticated_duplicate_company(self):
        """
        Test for trying to create a company that already exists.
        """

        company_count = Company.objects.count()
        url = reverse("company-list")
        data = {
            "name": "Red company BV",
            "vat_number": "VATRED",
            "business_registration_number": "NL123456"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Company.objects.count(), company_count)