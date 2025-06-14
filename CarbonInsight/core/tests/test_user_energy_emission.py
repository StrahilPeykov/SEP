"""
Tests for user energy emission API
"""

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
from core.tests.setup_functions import paint_companies_setup

User = get_user_model()


class UserEnergyEmissionAPITests(APITestCase):
    def setUp(self):
        paint_companies_setup(self)

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

        self.user_ref_grid_electricity = UserEnergyEmissionReference.objects.create(
            common_name="User Grid Electricity (EU Average)"
        )
        UserEnergyEmissionReferenceFactor.objects.create(
            emission_reference=self.user_ref_grid_electricity,
            lifecycle_stage=LifecycleStage.B1,
            co_2_emission_factor_biogenic=0.25
        )

        self.user_ref_solar_energy = UserEnergyEmissionReference.objects.create(
            common_name="User Solar Energy (On-site)"
        )
        UserEnergyEmissionReferenceFactor.objects.create(
            emission_reference=self.user_ref_solar_energy,
            lifecycle_stage=LifecycleStage.B1,
            co_2_emission_factor_biogenic=0.04
        )

        self.existing_user_emission_red_product = UserEnergyEmission.objects.create(
            parent_product=self.red_paint,
            energy_consumption=100.0,
            reference=self.user_ref_grid_electricity,
        )
        self.existing_user_emission_red_product.override_factors.create(
            lifecycle_stage=LifecycleStage.B1, co_2_emission_factor_biogenic=0.20
        )

        self.existing_user_emission_green_product = UserEnergyEmission.objects.create(
            parent_product=self.green_paint,
            energy_consumption=50.0,
            reference=self.user_ref_solar_energy,
        )

    def test_create_user_emission_unauthenticated(self):
        """
        Test for adding user energy emission to a product without logging in.
        """

        self.client.credentials()
        url = reverse(
            "product-user-energy-emissions-list",
            args=[self.red_company.id, self.red_paint.id]
        )
        data = {
            "energy_consumption": 75.0,
            "reference": self.user_ref_grid_electricity.id,
            "override_factors": []
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_user_emission_authenticated_authorized(self):
        """
        Test for adding user energy emission to a product that the user's company owns.
        """

        url = reverse(
            "product-user-energy-emissions-list",
            args=[self.red_company.id, self.red_paint.id]
        )
        data = {
            "energy_consumption": 75.0,
            "reference": self.user_ref_grid_electricity.id,
            "override_factors": [{"lifecycle_stage": LifecycleStage.OTHER, "co_2_emission_factor_biogenic": 0.01}]
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserEnergyEmission.objects.count(), 3)

    def test_create_user_emission_authenticated_unauthorized(self):
        """
        Test for adding user energy emission to a product that the user's company does not own.
        """

        url = reverse(
            "product-user-energy-emissions-list",
            args=[self.green_company.id, self.green_paint.id]
        )
        data = {
            "energy_consumption": 75.0,
            "reference": self.user_ref_grid_electricity.id,
            "override_factors": []
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_user_emission_invalid_data(self):
        """
        Test for adding user energy emission with invalid data.
        """

        url = reverse(
            "product-user-energy-emissions-list",
            args=[self.red_company.id, self.red_paint.id]
        )
        data_invalid_energy = {
            "energy_consumption": -10.0,
            "reference": self.user_ref_grid_electricity.id,
            "override_factors": []
        }
        response = self.client.post(url, data_invalid_energy, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_emission_product_not_found(self):
        """
        Test for creating user energy emissions list on a product that does not exist.
        """

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
        """
        Test for modifying a user energy emission without logging in with a put request.
        """

        self.client.credentials()
        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_user_emission_red_product.id]
        )
        data = {
            "energy_consumption": 120.0,
            "reference": self.user_ref_solar_energy.id,
            "override_factors": []
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_user_emission_authenticated_authorized(self):
        """
        Test for modifying a user energy emission of a product that the user's company owns with a put request.
        """

        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_user_emission_red_product.id]
        )
        data = {
            "energy_consumption": 120.0,
            "reference": self.user_ref_solar_energy.id,
            "override_factors": [{"lifecycle_stage": LifecycleStage.A1A3, "co_2_emission_factor_biogenic": 0.02}]
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.existing_user_emission_red_product.refresh_from_db()
        self.assertEqual(self.existing_user_emission_red_product.energy_consumption, 120.0)

    def test_put_user_emission_authenticated_unauthorized(self):
        """
        Test for modifying a user energy emission of a product that the user's company does not own with a put
         request.
        """

        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.green_company.id, self.green_paint.id, self.existing_user_emission_green_product.id]
        )
        data = {
            "energy_consumption": 60.0,
            "reference": self.user_ref_grid_electricity.id,
            "override_factors": []
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_user_emission_not_found(self):
        """
        Test for modifying a production energy emission of a product that does not exist with a put request.
        """

        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, 9999]
        )
        data = {
            "energy_consumption": 120.0,
            "reference": self.user_ref_grid_electricity.id,
            "override_factors": []
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_user_emission_invalid_data(self):
        """
        Test for modifying a production energy emission with a put request that has invalid data.
        """

        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_user_emission_red_product.id]
        )
        data_invalid_energy = {
            "energy_consumption": -5.0,
            "reference": self.user_ref_grid_electricity.id,
            "override_factors": []
        }
        response = self.client.put(url, data_invalid_energy, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_user_emission_mismatch_product_in_url(self):
        """
        Crash test for trying to query a wrong product url in put API.
        """

        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.purple_paint.id, self.existing_user_emission_red_product.id]
        )
        data = {
            "energy_consumption": 130.0,
            "reference": self.user_ref_grid_electricity.id,
            "override_factors": []
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_user_emission_unauthenticated(self):
        """
        Test for modifying a user energy emission without logging in with a patch request.
        """

        self.client.credentials()
        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_user_emission_red_product.id]
        )
        data = {
            "energy_consumption": 110.0,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_user_emission_authenticated_authorized(self):
        """
        Test for modifying a user energy emission of a product that the user's company owns with a patch request.
        """

        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_user_emission_red_product.id]
        )
        data = {
            "energy_consumption": 110.0,
            "override_factors": [{"lifecycle_stage": LifecycleStage.A2, "co_2_emission_factor_biogenic": 0.005}]
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.existing_user_emission_red_product.refresh_from_db()
        self.assertEqual(self.existing_user_emission_red_product.energy_consumption, 110.0)

    def test_patch_user_emission_authenticated_unauthorized(self):
        """
        Test for modifying a user energy emission of a product that the user's company does not own with a patch
         request.
        """

        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.green_company.id, self.green_paint.id, self.existing_user_emission_green_product.id]
        )
        data = {
            "energy_consumption": 55.0,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_user_emission_not_found(self):
        """
        Test for modifying a production energy emission of a product that does not exist with a patch request.
        """

        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, 9999]
        )
        data = {
            "energy_consumption": 110.0,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_user_emission_invalid_data(self):
        """
        Test for modifying a production energy emission with a patch request that has invalid data.
        """

        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_user_emission_red_product.id]
        )
        data_invalid_energy = {
            "energy_consumption": -5.0,
        }
        response = self.client.patch(url, data_invalid_energy, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_user_emission_mismatch_product_in_url(self):
        """
        Crash test for trying to query a wrong product url in patch API.
        """

        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.purple_paint.id, self.existing_user_emission_red_product.id]
        )
        data = {
            "energy_consumption": 115.0,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_user_emission_unauthenticated(self):
        """
        Test for deleting a user energy emission without logging in.
        """

        self.client.credentials()
        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_user_emission_red_product.id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(UserEnergyEmission.objects.count(), 2)

    def test_delete_user_emission_authenticated_authorized(self):
        """
        Test for deleting a user energy emission of a product that the user's company owns.
        """

        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, self.existing_user_emission_red_product.id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(UserEnergyEmission.objects.count(), 1)

    def test_delete_user_emission_authenticated_unauthorized(self):
        """
        Test for deleting a user energy emission of a product that the user's company does not own.
        """

        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.green_company.id, self.green_paint.id, self.existing_user_emission_green_product.id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(UserEnergyEmission.objects.count(), 2)

    def test_delete_user_emission_not_found(self):
        """
        Test for deleting a production energy emission of a product that does not exist.
        """

        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.red_paint.id, 9999]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(UserEnergyEmission.objects.count(), 2)

    def test_delete_user_emission_mismatch_product_in_url(self):
        """
        Crash test for trying to query a wrong product url in delete API.
        """

        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.purple_paint.id, self.existing_user_emission_red_product.id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(UserEnergyEmission.objects.count(), 2)
