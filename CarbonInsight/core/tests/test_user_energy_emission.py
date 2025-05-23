from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from core.models import ProductBoMLineItem
from core.models.company import Company
from core.models.company_membership import CompanyMembership
from core.models.product import Product
from core.models.user_energy_emission import UserEnergyEmission, UserEnergyEmissionReference, UserEnergyEmissionReferenceFactor
from core.models.lifecycle_stage import LifecycleStage


User = get_user_model()


class UserEnergyEmissionAPITests(APITestCase):
    def setUp(self):
        self.red_company_user1 = User.objects.create_user(username="1@redcompany.com", email="1@redcompany.com", password="1234567890")
        User.objects.create_user(username="2@redcompany.com", email="2@redcompany.com", password="1234567890")
        User.objects.create_user(username="1@greencompany.com", email="1@greencompany.com", password="1234567890")
        User.objects.create_user(username="2@greencompany.com", email="2@greencompany.com", password="1234567890")

        url = reverse("token_obtain_pair")
        resp = self.client.post(
            url, {"username": "1@redcompany.com", "password": "1234567890"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.access_token = resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

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

        CompanyMembership.objects.create(user=self.red_company_user1, company=self.red_company)

        self.red_company_product1 = Product.objects.create(
            name="Red Product 1 (Parent for BOM)",
            description="Description for Red Product 1",
            supplier=self.red_company,
            manufacturer_name="Red Manufacturer",
            manufacturer_country="NL",
            manufacturer_city="Eindhoven",
            manufacturer_street="Street 1",
            manufacturer_zip_code="1234AB",
            year_of_construction=2025,
            family="General",
            sku="REDPROD001",
            is_public=True
        )
        self.red_company_product2 = Product.objects.create(
            name="Red Product 2",
            description="Description for Red Product 2",
            supplier=self.red_company,
            manufacturer_name="Red Manufacturer",
            manufacturer_country="NL",
            manufacturer_city="Eindhoven",
            manufacturer_street="Street 2",
            manufacturer_zip_code="5678CD",
            year_of_construction=2025,
            family="General",
            sku="REDPROD002",
            is_public=True
        )

        # IMPORTANT: This product MUST be created in setUp for the BOM tests to work
        self.red_company_product_child = Product.objects.create(
            name="Child Product for BOM",
            description="A child product to be included in BOM",
            supplier=self.red_company,
            manufacturer_name="Test Manufacturer",
            manufacturer_country="NL",
            manufacturer_city="Utrecht",
            manufacturer_street="Child Street 1",
            manufacturer_zip_code="3500AA",
            year_of_construction=2024,
            family="Child Family",
            sku="SKU002",
            is_public=True
        )

        self.green_company_product1 = Product.objects.create(
            name="Green Product 1",
            description="Description for Green Product 1",
            supplier=self.green_company,
            manufacturer_name="Green Manufacturer",
            manufacturer_country="NL",
            manufacturer_city="Utrecht",
            manufacturer_street="Street 3",
            manufacturer_zip_code="9012EF",
            year_of_construction=2025,
            family="General",
            sku="GRNPROD001",
            is_public=True
        )

        self.user_ref_grid_electricity = UserEnergyEmissionReference.objects.create(
            common_name="User Grid Electricity (EU Average)"
        )
        UserEnergyEmissionReferenceFactor.objects.create(
            emission_reference=self.user_ref_grid_electricity,
            lifecycle_stage=LifecycleStage.B1,
            co_2_emission_factor=0.25
        )

        self.user_ref_solar_energy = UserEnergyEmissionReference.objects.create(
            common_name="User Solar Energy (On-site)"
        )
        UserEnergyEmissionReferenceFactor.objects.create(
            emission_reference=self.user_ref_solar_energy,
            lifecycle_stage=LifecycleStage.B1,
            co_2_emission_factor=0.04
        )

        self.existing_user_emission_red_product = UserEnergyEmission.objects.create(
            parent_product=self.red_company_product1,
            energy_consumption=100.0,
            reference=self.user_ref_grid_electricity,
        )
        self.existing_user_emission_red_product.override_factors.create(
            lifecycle_stage=LifecycleStage.B1, co_2_emission_factor=0.20
        )

        self.existing_user_emission_green_product = UserEnergyEmission.objects.create(
            parent_product=self.green_company_product1,
            energy_consumption=50.0,
            reference=self.user_ref_solar_energy,
        )

    def test_create_user_emission_unauthenticated(self):
        self.client.credentials()
        url = reverse(
            "product-user-energy-emissions-list",
            args=[self.red_company.id, self.red_company_product1.id]
        )
        data = {
            "energy_consumption": 75.0,
            "reference": self.user_ref_grid_electricity.id,
            "override_factors": []
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_user_emission_authenticated_authorized(self):
        url = reverse(
            "product-user-energy-emissions-list",
            args=[self.red_company.id, self.red_company_product1.id]
        )
        data = {
            "energy_consumption": 75.0,
            "reference": self.user_ref_grid_electricity.id,
            "override_factors": [{"lifecycle_stage": LifecycleStage.OTHER, "co_2_emission_factor": 0.01}]
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserEnergyEmission.objects.count(), 3)

    def test_create_user_emission_authenticated_unauthorized(self):
        url = reverse(
            "product-user-energy-emissions-list",
            args=[self.green_company.id, self.green_company_product1.id]
        )
        data = {
            "energy_consumption": 75.0,
            "reference": self.user_ref_grid_electricity.id,
            "override_factors": []
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_user_emission_invalid_data(self):
        url = reverse(
            "product-user-energy-emissions-list",
            args=[self.red_company.id, self.red_company_product1.id]
        )
        data_invalid_energy = {
            "energy_consumption": -10.0,
            "reference": self.user_ref_grid_electricity.id,
            "override_factors": []
        }
        response = self.client.post(url, data_invalid_energy, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_emission_product_not_found(self):
        url = reverse(
            "product-user-energy-emissions-list",
            args=[self.red_company.id, 9999]
        )
        data = {
            "energy_consumption": 50.0,
            "reference": self.user_ref_grid_electricity.id,
            "override_factors": []
        }
        response = self.client.post(url, data, format="json")
        self.assertIn(response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])

    def test_put_user_emission_unauthenticated(self):
        self.client.credentials()
        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.red_company_product1.id, self.existing_user_emission_red_product.id]
        )
        data = {
            "energy_consumption": 120.0,
            "reference": self.user_ref_solar_energy.id,
            "override_factors": []
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_user_emission_authenticated_authorized(self):
        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.red_company_product1.id, self.existing_user_emission_red_product.id]
        )
        data = {
            "energy_consumption": 120.0,
            "reference": self.user_ref_solar_energy.id,
            "override_factors": [{"lifecycle_stage": LifecycleStage.A1A3, "co_2_emission_factor": 0.02}]
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.existing_user_emission_red_product.refresh_from_db()
        self.assertEqual(self.existing_user_emission_red_product.energy_consumption, 120.0)

    def test_put_user_emission_authenticated_unauthorized(self):
        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.green_company.id, self.green_company_product1.id, self.existing_user_emission_green_product.id]
        )
        data = {
            "energy_consumption": 60.0,
            "reference": self.user_ref_grid_electricity.id,
            "override_factors": []
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_user_emission_not_found(self):
        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.red_company_product1.id, 9999]
        )
        data = {
            "energy_consumption": 120.0,
            "reference": self.user_ref_grid_electricity.id,
            "override_factors": []
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_user_emission_invalid_data(self):
        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.red_company_product1.id, self.existing_user_emission_red_product.id]
        )
        data_invalid_energy = {
            "energy_consumption": -5.0,
            "reference": self.user_ref_grid_electricity.id,
            "override_factors": []
        }
        response = self.client.put(url, data_invalid_energy, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_user_emission_mismatch_product_in_url(self):
        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.red_company_product2.id, self.existing_user_emission_red_product.id]
        )
        data = {
            "energy_consumption": 130.0,
            "reference": self.user_ref_grid_electricity.id,
            "override_factors": []
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_user_emission_unauthenticated(self):
        self.client.credentials()
        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.red_company_product1.id, self.existing_user_emission_red_product.id]
        )
        data = {
            "energy_consumption": 110.0,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_user_emission_authenticated_authorized(self):
        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.red_company_product1.id, self.existing_user_emission_red_product.id]
        )
        data = {
            "energy_consumption": 110.0,
            "override_factors": [{"lifecycle_stage": LifecycleStage.A2, "co_2_emission_factor": 0.005}]
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.existing_user_emission_red_product.refresh_from_db()
        self.assertEqual(self.existing_user_emission_red_product.energy_consumption, 110.0)

    def test_patch_user_emission_authenticated_unauthorized(self):
        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.green_company.id, self.green_company_product1.id, self.existing_user_emission_green_product.id]
        )
        data = {
            "energy_consumption": 55.0,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_user_emission_not_found(self):
        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.red_company_product1.id, 9999]
        )
        data = {
            "energy_consumption": 110.0,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_user_emission_invalid_data(self):
        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.red_company_product1.id, self.existing_user_emission_red_product.id]
        )
        data_invalid_energy = {
            "energy_consumption": -5.0,
        }
        response = self.client.patch(url, data_invalid_energy, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_user_emission_mismatch_product_in_url(self):
        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.red_company_product2.id, self.existing_user_emission_red_product.id]
        )
        data = {
            "energy_consumption": 115.0,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_user_emission_unauthenticated(self):
        self.client.credentials()
        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.red_company_product1.id, self.existing_user_emission_red_product.id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(UserEnergyEmission.objects.count(), 2)

    def test_delete_user_emission_authenticated_authorized(self):
        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.red_company_product1.id, self.existing_user_emission_red_product.id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(UserEnergyEmission.objects.count(), 1)

    def test_delete_user_emission_authenticated_unauthorized(self):
        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.green_company.id, self.green_company_product1.id, self.existing_user_emission_green_product.id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(UserEnergyEmission.objects.count(), 2)

    def test_delete_user_emission_not_found(self):
        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.red_company_product1.id, 9999]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(UserEnergyEmission.objects.count(), 2)

    def test_delete_user_emission_mismatch_product_in_url(self):
        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.red_company_product2.id, self.existing_user_emission_red_product.id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(UserEnergyEmission.objects.count(), 2)
