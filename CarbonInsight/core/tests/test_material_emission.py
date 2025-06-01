from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from core.models.company import Company
from core.models.company_membership import CompanyMembership
from core.models.product import Product
from core.models.lifecycle_stage import LifecycleStage
from core.models.material_emission import (
    MaterialEmission,
    MaterialEmissionReference,
    MaterialEmissionReferenceFactor,
)
from core.tests.setup_functions import paint_companies_setup

User = get_user_model()


class MaterialEmissionAPITests(APITestCase):
    def setUp(self):
        paint_companies_setup(self)

        self.mat_ref_steel = MaterialEmissionReference.objects.create(
            common_name="Steel (Generic)"
        )
        MaterialEmissionReferenceFactor.objects.create(
            emission_reference=self.mat_ref_steel,
            lifecycle_stage=LifecycleStage.A1A3,
            co_2_emission_factor_biogenic=1.9
        )

        self.existing_mat_emission_red_product = MaterialEmission.objects.create(
            parent_product=self.red_paint,
            weight=10.0,
            reference=self.mat_ref_steel,
        )

        self.existing_mat_emission_green_product = MaterialEmission.objects.create(
            parent_product=self.green_paint,
            weight=5.0,
            reference=self.mat_ref_steel,
        )

    def test_create_material_emission_unauthenticated(self):
        self.client.credentials()
        url = reverse(
            "product-material-emissions-list",
            args=[self.red_company.id, self.red_paint.id]
        )
        data = {
            "weight": 15.0,
            "reference": self.mat_ref_steel.id,
            "override_factors": []
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_material_emission_authenticated_authorized(self):
        url = reverse(
            "product-material-emissions-list",
            args=[self.red_company.id, self.red_paint.id]
        )
        data = {
            "weight": 15.0,
            "reference": self.mat_ref_steel.id,
            "override_factors": []
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MaterialEmission.objects.count(), 3)

    def test_create_material_emission_authenticated_unauthorized(self):
        url = reverse(
            "product-material-emissions-list",
            args=[self.green_company.id, self.green_paint.id]
        )
        data = {
            "weight": 15.0,
            "reference": self.mat_ref_steel.id,
            "override_factors": []
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_material_emission_invalid_data(self):
        url = reverse(
            "product-material-emissions-list",
            args=[self.red_company.id, self.red_paint.id]
        )
        data = {
            "weight": -5.0,
            "reference": self.mat_ref_steel.id,
            "override_factors": []
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_material_emissions_list_unauthenticated(self):
        self.client.credentials()
        url = reverse(
            "product-material-emissions-list",
            args=[self.red_company.id, self.red_paint.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_material_emissions_list_authenticated_authorized(self):
        url = reverse(
            "product-material-emissions-list",
            args=[self.red_company.id, self.red_paint.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.existing_mat_emission_red_product.id)

    def test_get_material_emissions_list_authenticated_unauthorized(self):
        url = reverse(
            "product-material-emissions-list",
            args=[self.green_company.id, self.green_paint.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_material_emission_detail_unauthenticated(self):
        self.client.credentials()
        url = reverse(
            "product-material-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_mat_emission_red_product.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_material_emission_detail_authenticated_authorized(self):
        url = reverse(
            "product-material-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_mat_emission_red_product.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.existing_mat_emission_red_product.id)

    def test_get_material_emission_detail_authenticated_unauthorized(self):
        url = reverse(
            "product-material-emissions-detail",
            args=[self.green_company.id, self.green_paint.id, self.existing_mat_emission_green_product.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_material_emission_unauthenticated(self):
        self.client.credentials()
        url = reverse(
            "product-material-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_mat_emission_red_product.id]
        )
        data = {
            "weight": 20.0,
            "reference": self.mat_ref_steel.id,
            "override_factors": []
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_material_emission_authenticated_authorized(self):
        url = reverse(
            "product-material-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_mat_emission_red_product.id]
        )
        data = {
            "weight": 20.0,
            "reference": self.mat_ref_steel.id,
            "override_factors": []
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.existing_mat_emission_red_product.refresh_from_db()
        self.assertEqual(self.existing_mat_emission_red_product.weight, 20.0)

    def test_put_material_emission_authenticated_unauthorized(self):
        url = reverse(
            "product-material-emissions-detail",
            args=[self.green_company.id, self.green_paint.id, self.existing_mat_emission_green_product.id]
        )
        data = {
            "weight": 12.0,
            "reference": self.mat_ref_steel.id,
            "override_factors": []
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_material_emission_unauthenticated(self):
        self.client.credentials()
        url = reverse(
            "product-material-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_mat_emission_red_product.id]
        )
        data = {"weight": 18.0}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_material_emission_authenticated_authorized(self):
        url = reverse(
            "product-material-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_mat_emission_red_product.id]
        )
        data = {"weight": 18.0, "override_factors": []}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.existing_mat_emission_red_product.refresh_from_db()
        self.assertEqual(self.existing_mat_emission_red_product.weight, 18.0)

    def test_patch_material_emission_authenticated_unauthorized(self):
        url = reverse(
            "product-material-emissions-detail",
            args=[self.green_company.id, self.green_paint.id, self.existing_mat_emission_green_product.id]
        )
        data = {"weight": 11.0}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_material_emission_unauthenticated(self):
        self.client.credentials()
        url = reverse(
            "product-material-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_mat_emission_red_product.id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(MaterialEmission.objects.count(), 2)

    def test_delete_material_emission_authenticated_authorized(self):
        url = reverse(
            "product-material-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_mat_emission_red_product.id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(MaterialEmission.objects.count(), 1)

    def test_delete_material_emission_authenticated_unauthorized(self):
        url = reverse(
            "product-material-emissions-detail",
            args=[self.green_company.id, self.green_paint.id,
                  self.existing_mat_emission_green_product.id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(MaterialEmission.objects.count(), 2)