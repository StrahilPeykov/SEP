from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from core.models.company import Company
from core.models.company_membership import CompanyMembership
from core.models.product import Product
from core.models.transport_emission import (
    TransportEmission,
    TransportEmissionReference,
    TransportEmissionReferenceFactor,
)
from core.tests.setup_functions import paint_companies_setup

User = get_user_model()


class TransportEmissionAPITests(APITestCase):
    def setUp(self):
        paint_companies_setup(self)

        self.transport_ref_truck = TransportEmissionReference.objects.create(
            common_name="Truck Transport"
        )
        TransportEmissionReferenceFactor.objects.create(
            emission_reference=self.transport_ref_truck,
            lifecycle_stage="A1A3",
            co_2_emission_factor_biogenic=0.1
        )

        self.existing_transport_emission_red_product = TransportEmission.objects.create(
            parent_product=self.red_paint,
            distance=100.0,
            weight=1000.0,
            reference=self.transport_ref_truck,
        )

        self.existing_transport_emission_green_product = TransportEmission.objects.create(
            parent_product=self.green_paint,
            distance=50.0,
            weight=2000.0,
            reference=self.transport_ref_truck,
        )

    def test_create_transport_emission_unauthenticated(self):
        self.client.credentials()
        url = reverse(
            "product-transport-emissions-list",
            args=[self.red_company.id, self.red_paint.id]
        )
        data = {
            "distance": 150.0,
            "weight": 500.0,
            "reference": self.transport_ref_truck.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_transport_emission_authenticated_authorized(self):
        url = reverse(
            "product-transport-emissions-list",
            args=[self.red_company.id, self.red_paint.id]
        )
        data = {
            "distance": 150.0,
            "weight": 500.0,
            "reference": self.transport_ref_truck.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TransportEmission.objects.count(), 3)

    def test_create_transport_emission_authenticated_unauthorized(self):
        url = reverse(
            "product-transport-emissions-list",
            args=[self.green_company.id, self.green_paint.id]
        )
        data = {
            "distance": 150.0,
            "weight": 500.0,
            "reference": self.transport_ref_truck.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_transport_emission_invalid_data(self):
        url = reverse(
            "product-transport-emissions-list",
            args=[self.red_company.id, self.red_paint.id]
        )
        data = {
            "distance": -5.0,
            "weight": 500.0,
            "reference": self.transport_ref_truck.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_transport_emissions_list_unauthenticated(self):
        self.client.credentials()
        url = reverse(
            "product-transport-emissions-list",
            args=[self.red_company.id, self.red_paint.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_transport_emissions_list_authenticated_authorized(self):
        url = reverse(
            "product-transport-emissions-list",
            args=[self.red_company.id, self.red_paint.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.existing_transport_emission_red_product.id)

    def test_get_transport_emissions_list_authenticated_unauthorized(self):
        url = reverse(
            "product-transport-emissions-list",
            args=[self.green_company.id, self.green_paint.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_transport_emission_detail_unauthenticated(self):
        self.client.credentials()
        url = reverse(
            "product-transport-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_transport_emission_red_product.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_transport_emission_detail_authenticated_authorized(self):
        url = reverse(
            "product-transport-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_transport_emission_red_product.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.existing_transport_emission_red_product.id)

    def test_get_transport_emission_detail_authenticated_unauthorized(self):
        url = reverse(
            "product-transport-emissions-detail",
            args=[self.green_company.id, self.green_paint.id, self.existing_transport_emission_green_product.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_transport_emission_unauthenticated(self):
        self.client.credentials()
        url = reverse(
            "product-transport-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_transport_emission_red_product.id]
        )
        data = {
            "distance": 200.0,
            "weight": 750.0,
            "reference": self.transport_ref_truck.id,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_transport_emission_authenticated_authorized(self):
        url = reverse(
            "product-transport-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_transport_emission_red_product.id]
        )
        data = {
            "distance": 200.0,
            "weight": 750.0,
            "reference": self.transport_ref_truck.id,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.existing_transport_emission_red_product.refresh_from_db()
        self.assertEqual(self.existing_transport_emission_red_product.distance, 200.0)
        self.assertEqual(self.existing_transport_emission_red_product.weight, 750.0)

    def test_put_transport_emission_authenticated_unauthorized(self):
        url = reverse(
            "product-transport-emissions-detail",
            args=[self.green_company.id, self.green_paint.id, self.existing_transport_emission_green_product.id]
        )
        data = {
            "distance": 100.0,
            "weight": 1500.0,
            "reference": self.transport_ref_truck.id,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_transport_emission_unauthenticated(self):
        self.client.credentials()
        url = reverse(
            "product-transport-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_transport_emission_red_product.id]
        )
        data = {"distance": 180.0}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_transport_emission_authenticated_authorized(self):
        url = reverse(
            "product-transport-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_transport_emission_red_product.id]
        )
        data = {"distance": 180.0}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.existing_transport_emission_red_product.refresh_from_db()
        self.assertEqual(self.existing_transport_emission_red_product.distance, 180.0)

    def test_patch_transport_emission_authenticated_unauthorized(self):
        url = reverse(
            "product-transport-emissions-detail",
            args=[self.green_company.id, self.green_paint.id, self.existing_transport_emission_green_product.id]
        )
        data = {"distance": 75.0}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_transport_emission_unauthenticated(self):
        self.client.credentials()
        url = reverse(
            "product-transport-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_transport_emission_red_product.id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(TransportEmission.objects.count(), 2)

    def test_delete_transport_emission_authenticated_authorized(self):
        url = reverse(
            "product-transport-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_transport_emission_red_product.id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TransportEmission.objects.count(), 1)

    def test_delete_transport_emission_authenticated_unauthorized(self):
        url = reverse(
            "product-transport-emissions-detail",
            args=[self.green_company.id, self.green_paint.id, self.existing_transport_emission_green_product.id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(TransportEmission.objects.count(), 2)