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

User = get_user_model()


class MaterialEmissionAPITests(APITestCase):
    def setUp(self):
        self.red_company_user1 = User.objects.create_user(username="1@redcompany.com", email="1@redcompany.com", password="1234567890")

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
            name="Red Product 1",
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

        self.mat_ref_steel = MaterialEmissionReference.objects.create(
            common_name="Steel (Generic)"
        )
        MaterialEmissionReferenceFactor.objects.create(
            emission_reference=self.mat_ref_steel,
            lifecycle_stage=LifecycleStage.A1A3,
            co_2_emission_factor=1.9
        )

        self.existing_mat_emission_red_product = MaterialEmission.objects.create(
            parent_product=self.red_company_product1,
            weight=10.0,
            reference=self.mat_ref_steel,
        )

        self.existing_mat_emission_green_product = MaterialEmission.objects.create(
            parent_product=self.green_company_product1,
            weight=5.0,
            reference=self.mat_ref_steel,
        )

    def test_create_material_emission_unauthenticated(self):
        self.client.credentials()
        url = reverse(
            "product-material-emissions-list",
            args=[self.red_company.id, self.red_company_product1.id]
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
            args=[self.red_company.id, self.red_company_product1.id]
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
            args=[self.green_company.id, self.green_company_product1.id]
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
            args=[self.red_company.id, self.red_company_product1.id]
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
            args=[self.red_company.id, self.red_company_product1.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_material_emissions_list_authenticated_authorized(self):
        url = reverse(
            "product-material-emissions-list",
            args=[self.red_company.id, self.red_company_product1.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.existing_mat_emission_red_product.id)

    def test_get_material_emissions_list_authenticated_unauthorized(self):
        url = reverse(
            "product-material-emissions-list",
            args=[self.green_company.id, self.green_company_product1.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_material_emission_detail_unauthenticated(self):
        self.client.credentials()
        url = reverse(
            "product-material-emissions-detail",
            args=[self.red_company.id, self.red_company_product1.id, self.existing_mat_emission_red_product.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_material_emission_detail_authenticated_authorized(self):
        url = reverse(
            "product-material-emissions-detail",
            args=[self.red_company.id, self.red_company_product1.id, self.existing_mat_emission_red_product.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.existing_mat_emission_red_product.id)

    def test_get_material_emission_detail_authenticated_unauthorized(self):
        url = reverse(
            "product-material-emissions-detail",
            args=[self.green_company.id, self.green_company_product1.id, self.existing_mat_emission_green_product.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_material_emission_unauthenticated(self):
        self.client.credentials()
        url = reverse(
            "product-material-emissions-detail",
            args=[self.red_company.id, self.red_company_product1.id, self.existing_mat_emission_red_product.id]
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
            args=[self.red_company.id, self.red_company_product1.id, self.existing_mat_emission_red_product.id]
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
            args=[self.green_company.id, self.green_company_product1.id, self.existing_mat_emission_green_product.id]
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
            args=[self.red_company.id, self.red_company_product1.id, self.existing_mat_emission_red_product.id]
        )
        data = {"weight": 18.0}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_material_emission_authenticated_authorized(self):
        url = reverse(
            "product-material-emissions-detail",
            args=[self.red_company.id, self.red_company_product1.id, self.existing_mat_emission_red_product.id]
        )
        data = {"weight": 18.0, "override_factors": []}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.existing_mat_emission_red_product.refresh_from_db()
        self.assertEqual(self.existing_mat_emission_red_product.weight, 18.0)

    def test_patch_material_emission_authenticated_unauthorized(self):
        url = reverse(
            "product-material-emissions-detail",
            args=[self.green_company.id, self.green_company_product1.id, self.existing_mat_emission_green_product.id]
        )
        data = {"weight": 11.0}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_material_emission_unauthenticated(self):
        self.client.credentials()
        url = reverse(
            "product-material-emissions-detail",
            args=[self.red_company.id, self.red_company_product1.id, self.existing_mat_emission_red_product.id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(MaterialEmission.objects.count(), 2)

    def test_delete_material_emission_authenticated_authorized(self):
        url = reverse(
            "product-material-emissions-detail",
            args=[self.red_company.id, self.red_company_product1.id, self.existing_mat_emission_red_product.id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(MaterialEmission.objects.count(), 1)

    def test_delete_material_emission_authenticated_unauthorized(self):
        url = reverse(
            "product-material-emissions-detail",
            args=[self.green_company.id, self.green_company_product1.id,
                  self.existing_mat_emission_green_product.id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(MaterialEmission.objects.count(), 2)