from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from core.models.company import Company
from core.models.company_membership import CompanyMembership
from core.models.product import Product
from core.models.lifecycle_stage import LifecycleStage
from core.models.production_energy_emission import (
    ProductionEnergyEmission,
    ProductionEnergyEmissionReference,
    ProductionEnergyEmissionReferenceFactor,
)
from core.tests.setup_functions import paint_companies_setup

User = get_user_model()


class ProductionEnergyEmissionAPITests(APITestCase):
    def setUp(self):
        paint_companies_setup(self)

        self.prod_ref_electricity = ProductionEnergyEmissionReference.objects.create(
            common_name="Production Electricity (Generic)"
        )
        ProductionEnergyEmissionReferenceFactor.objects.create(
            emission_reference=self.prod_ref_electricity,
            lifecycle_stage=LifecycleStage.A1A3,
            co_2_emission_factor_biogenic=0.15
        )

        self.existing_prod_emission_red_product = ProductionEnergyEmission.objects.create(
            parent_product=self.red_paint,
            energy_consumption=200.0,
            reference=self.prod_ref_electricity,
        )

        self.existing_prod_emission_green_product = ProductionEnergyEmission.objects.create(
            parent_product=self.green_paint,
            energy_consumption=100.0,
            reference=self.prod_ref_electricity,
        )

    def test_create_production_emission_unauthenticated(self):
        self.client.credentials()
        url = reverse(
            "product-production-energy-emissions-list",
            args=[self.red_company.id, self.red_paint.id]
        )
        data = {
            "energy_consumption": 150.0,
            "reference": self.prod_ref_electricity.id,
            "override_factors": []
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_production_emission_authenticated_authorized(self):
        url = reverse(
            "product-production-energy-emissions-list",
            args=[self.red_company.id, self.red_paint.id]
        )
        data = {
            "energy_consumption": 150.0,
            "reference": self.prod_ref_electricity.id,
            "override_factors": []
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductionEnergyEmission.objects.count(), 3)

    def test_create_production_emission_authenticated_unauthorized(self):
        url = reverse(
            "product-production-energy-emissions-list",
            args=[self.green_company.id, self.green_paint.id]
        )
        data = {
            "energy_consumption": 150.0,
            "reference": self.prod_ref_electricity.id,
            "override_factors": []
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_production_emission_invalid_data(self):
        url = reverse(
            "product-production-energy-emissions-list",
            args=[self.red_company.id, self.red_paint.id]
        )
        data = {
            "energy_consumption": -10.0,
            "reference": self.prod_ref_electricity.id,
            "override_factors": []
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_production_emissions_list_unauthenticated(self):
        self.client.credentials()
        url = reverse(
            "product-production-energy-emissions-list",
            args=[self.red_company.id, self.red_paint.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_production_emissions_list_authenticated_authorized(self):
        url = reverse(
            "product-production-energy-emissions-list",
            args=[self.red_company.id, self.red_paint.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.existing_prod_emission_red_product.id)

    def test_get_production_emissions_list_authenticated_unauthorized(self):
        url = reverse(
            "product-production-energy-emissions-list",
            args=[self.green_company.id, self.green_paint.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_production_emission_detail_unauthenticated(self):
        self.client.credentials()
        url = reverse(
            "product-production-energy-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_prod_emission_red_product.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_production_emission_detail_authenticated_authorized(self):
        url = reverse(
            "product-production-energy-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_prod_emission_red_product.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.existing_prod_emission_red_product.id)

    def test_get_production_emission_detail_authenticated_unauthorized(self):
        url = reverse(
            "product-production-energy-emissions-detail",
            args=[self.green_company.id, self.green_paint.id, self.existing_prod_emission_green_product.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_production_emission_unauthenticated(self):
        self.client.credentials()
        url = reverse(
            "product-production-energy-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_prod_emission_red_product.id]
        )
        data = {
            "energy_consumption": 250.0,
            "reference": self.prod_ref_electricity.id,
            "override_factors": []
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_production_emission_authenticated_authorized(self):
        url = reverse(
            "product-production-energy-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_prod_emission_red_product.id]
        )
        data = {
            "energy_consumption": 250.0,
            "reference": self.prod_ref_electricity.id,
            "override_factors": []
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.existing_prod_emission_red_product.refresh_from_db()
        self.assertEqual(self.existing_prod_emission_red_product.energy_consumption, 250.0)

    def test_put_production_emission_authenticated_unauthorized(self):
        url = reverse(
            "product-production-energy-emissions-detail",
            args=[self.green_company.id, self.green_paint.id, self.existing_prod_emission_green_product.id]
        )
        data = {
            "energy_consumption": 120.0,
            "reference": self.prod_ref_electricity.id,
            "override_factors": []
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_production_emission_unauthenticated(self):
        self.client.credentials()
        url = reverse(
            "product-production-energy-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_prod_emission_red_product.id]
        )
        data = {"energy_consumption": 220.0}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_production_emission_authenticated_authorized(self):
        url = reverse(
            "product-production-energy-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_prod_emission_red_product.id]
        )
        data = {"energy_consumption": 220.0, "override_factors": []}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.existing_prod_emission_red_product.refresh_from_db()
        self.assertEqual(self.existing_prod_emission_red_product.energy_consumption, 220.0)

    def test_patch_production_emission_authenticated_unauthorized(self):
        url = reverse(
            "product-production-energy-emissions-detail",
            args=[self.green_company.id, self.green_paint.id, self.existing_prod_emission_green_product.id]
        )
        data = {"energy_consumption": 110.0}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_production_emission_unauthenticated(self):
        self.client.credentials()
        url = reverse(
            "product-production-energy-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_prod_emission_red_product.id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(ProductionEnergyEmission.objects.count(), 2)

    def test_delete_production_emission_authenticated_authorized(self):
        url = reverse(
            "product-production-energy-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_prod_emission_red_product.id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ProductionEnergyEmission.objects.count(), 1)

    def test_delete_production_emission_authenticated_unauthorized(self):
        url = reverse(
            "product-production-energy-emissions-detail",
            args=[self.green_company.id, self.green_paint.id, self.existing_prod_emission_green_product.id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ProductionEnergyEmission.objects.count(), 2)