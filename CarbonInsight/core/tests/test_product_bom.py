"""
Tests for the Product BOM
"""

from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from core.models import CompanyMembership, Product, ProductBoMLineItem, \
    ProductionEnergyEmissionReference, EmissionBoMLink, ProductionEnergyEmission, UserEnergyEmissionReference, \
    UserEnergyEmission, LifecycleStage, \
    TransportEmissionReference, TransportEmissionReferenceFactor, TransportEmission
from core.tests.setup_functions import paint_companies_setup

User = get_user_model()

class ProductAPITest(APITestCase):
    def setUp(self):
        paint_companies_setup(self)

        self.product_for_emission_linking_parent = Product.objects.create(
            name="Product For Emission Linking Parent",
            supplier=self.red_company,
            manufacturer_name="Test Manufacturer",
            manufacturer_country="NL",
            manufacturer_city="Eindhoven",
            manufacturer_street="Test Street",
            manufacturer_zip_code="1234AB",
            year_of_construction=2025,
            family="Test",
            sku="EMLINK001",
            is_public=True
        )
        self.product_for_emission_linking_child = Product.objects.create(
            name="Product For Emission Linking Child",
            supplier=self.red_company,
            manufacturer_name="Test Manufacturer",
            manufacturer_country="NL",
            manufacturer_city="Eindhoven",
            manufacturer_street="Test Street",
            manufacturer_zip_code="1234AB",
            year_of_construction=2025,
            family="Test",
            sku="EMLINK002",
            is_public=True
        )
        self.product_for_emission_linking_other = Product.objects.create(
            name="Product For Emission Linking Other",
            supplier=self.red_company,
            manufacturer_name="Test Manufacturer",
            manufacturer_country="NL",
            manufacturer_city="Eindhoven",
            manufacturer_street="Test Street",
            manufacturer_zip_code="1234AB",
            year_of_construction=2025,
            family="Test",
            sku="EMLINK003",
            is_public=True
        )

        self.production_energy_ref = ProductionEnergyEmissionReference.objects.create(
            common_name="Test Production Energy Ref")

        self.user_energy_ref = UserEnergyEmissionReference.objects.create(common_name="Test User Energy Ref")

        self.transport_ref_ship = TransportEmissionReference.objects.create(
            common_name="Ship Transport (BOM Test)"
        )
        TransportEmissionReferenceFactor.objects.create(
            emission_reference=self.transport_ref_ship,
            lifecycle_stage=LifecycleStage.A4,
            co_2_emission_factor_biogenic=0.01
        )

    def test_emission_link_clean_method(self):
        """
        Test for trying to create a emission BoM link with different parent products test clean() and save() methods.
        """

        correct_bom_item = ProductBoMLineItem.objects.create(
            parent_product=self.purple_paint,
            line_item_product=self.blue_paint,
            quantity=1
        )
        wrong_bom_item = ProductBoMLineItem.objects.create(
            parent_product=self.magenta_paint,
            line_item_product=self.blue_paint,
            quantity=1
        )
        transport_emission = TransportEmission.objects.create(
            parent_product=self.purple_paint,
            distance=500.0,
            weight=100.0,
            reference=self.transport_ref_ship,
        )
        self.assertRaises(ValidationError, EmissionBoMLink.objects.create, **{
            "emission": transport_emission,
            "line_item": wrong_bom_item
        })

    def test_get_product_list_bom(self):
        """
        Tests retrieving a list of Bill of Materials (BOM) items for a product.
        """
        url = reverse("product-bom-list", args=[self.red_company.id, self.purple_paint.id])

        ProductBoMLineItem.objects.create(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=1
        )

        ProductBoMLineItem.objects.create(
            line_item_product=self.blue_paint,
            parent_product=self.purple_paint,
            quantity=1
        )

        response = self.client.get(url)
        returned_items = [response["line_item_product"]["name"] for response in response.data]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Red paint", returned_items)
        self.assertIn("Blue paint", returned_items)

    def test_get_product_list_bom_other_company(self):
        """
        Tests attempting to retrieve a BOM list for a product belonging to a different company.
        """
        url = reverse("product-bom-list", args=[self.blue_company.id, self.magenta_paint.id])

        ProductBoMLineItem.objects.create(
            line_item_product=self.red_paint,
            parent_product=self.magenta_paint,
            quantity=1
        )

        ProductBoMLineItem.objects.create(
            line_item_product=self.blue_paint,
            parent_product=self.magenta_paint,
            quantity=2
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_product_list_bom_other_company_crashtest(self):
        """
        Tests attempting to retrieve a BOM list for a product not associated with the specified company ID.
        """
        url = reverse("product-bom-list", args=[self.red_company.id, self.magenta_paint.id])

        ProductBoMLineItem.objects.create(
            line_item_product=self.red_paint,
            parent_product=self.magenta_paint,
            quantity=1
        )

        ProductBoMLineItem.objects.create(
            line_item_product=self.blue_paint,
            parent_product=self.magenta_paint,
            quantity=2
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_specific_product_bom(self):
        """
        Tests retrieving a specific Bill of Materials (BOM) item for a product.
        """
        item1 = ProductBoMLineItem.objects.create(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=1
        )

        item2 = ProductBoMLineItem.objects.create(
            line_item_product=self.blue_paint,
            parent_product=self.purple_paint,
            quantity=1
        )

        url1 = reverse("product-bom-detail", args=[
            self.red_company.id,
            self.purple_paint.id,
            item1.id
        ])

        url2 = reverse("product-bom-detail", args=[
            self.red_company.id,
            self.purple_paint.id,
            item2.id
        ])

        response1 = self.client.get(url1)
        response2 = self.client.get(url2)

        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data["line_item_product"]["name"], "Red paint")
        self.assertEqual(response2.data["line_item_product"]["name"], "Blue paint")

    def test_get_specific_product_bom_not_found(self):
        """
        Tests attempting to retrieve a non-existent specific BOM item.
        """
        url = reverse("product-bom-detail", args=[
            self.red_company.id,
            self.purple_paint.id,
            1
        ])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_specific_product_bom_other_company(self):
        """
        Tests attempting to retrieve a specific BOM item for a product belonging to a different company.
        """
        item1 = ProductBoMLineItem.objects.create(
            line_item_product=self.red_paint,
            parent_product=self.magenta_paint,
            quantity=1
        )

        ProductBoMLineItem.objects.create(
            line_item_product=self.blue_paint,
            parent_product=self.magenta_paint,
            quantity=2
        )

        url = reverse("product-bom-detail", args=[
            self.blue_company.id,
            self.magenta_paint.id,
            item1.id
        ])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_specific_product_bom_other_company_crashtest(self):
        """
        Tests attempting to retrieve a specific BOM item for a product not associated with the specified company ID.
        """
        item1 = ProductBoMLineItem.objects.create(
            line_item_product=self.red_paint,
            parent_product=self.magenta_paint,
            quantity=1
        )

        ProductBoMLineItem.objects.create(
            line_item_product=self.blue_paint,
            parent_product=self.magenta_paint,
            quantity=2
        )

        url = reverse("product-bom-detail", args=[
            self.red_company.id,
            self.magenta_paint.id,
            item1.id
        ])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_bom_line_item(self):
        """
        Tests creating a new Bill of Materials (BOM) line item for a product.
        """
        url = reverse("product-bom-list", args=[self.red_company.id, self.purple_paint.id])
        response = self.client.post(url, {
            "quantity": 1,
            "line_item_product_id": self.red_paint.id
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ProductBoMLineItem.objects.filter(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=1
        ).exists())

    def test_create_bom_line_item_missing_quantity(self):
        """
        Tests attempting to create a BOM line item with a missing quantity.
        """
        url = reverse("product-bom-list", args=[self.red_company.id, self.purple_paint.id])
        response = self.client.post(url, {
            "line_item_product_id": self.red_paint.id
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bom_line_item_missing_line_item_product_id(self):
        """
        Tests attempting to create a BOM line item with a missing line item product ID.
        """
        url = reverse("product-bom-list", args=[self.red_company.id, self.purple_paint.id])
        response = self.client.post(url, {
            "quantity": 1
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bom_line_item_other_company(self):
        """
        Tests attempting to create a BOM line item for a product belonging to a different company, expecting a 403 Forbidden.
        """
        url = reverse("product-bom-list", args=[self.blue_company.id, self.magenta_paint.id])
        response = self.client.post(url, {
            "quantity": 1,
            "line_item_product_id": self.red_paint.id
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(ProductBoMLineItem.objects.filter(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=1
        ).exists())

    def test_create_bom_line_item_other_company_crashtest(self):
        """
        Tests attempting to create a BOM line item for a product not associated with the specified company ID, expecting a 404 Not Found.
        """
        url = reverse("product-bom-list", args=[self.red_company.id, self.magenta_paint.id])
        response = self.client.post(url, {
            "quantity": 1,
            "line_item_product_id": self.red_paint.id
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(ProductBoMLineItem.objects.filter(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=1
        ).exists())

    def test_update_bom_line_item_with_line_item_product_id_fail(self):
        """
        Tests attempting to update a BOM line item by changing its line item product ID, which should fail.
        """
        item1 = ProductBoMLineItem.objects.create(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=2
        )
        initial_line_item_product_id = item1.line_item_product_id
        initial_quantity = item1.quantity

        url = reverse("product-bom-detail", args=[
            self.red_company.id,
            self.purple_paint.id,
            item1.id
        ])

        response = self.client.put(url, {
            "quantity": 1,
            "line_item_product_id": self.blue_paint.id
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data)
        found_line_item_error = False
        for error in response.data['errors']:
            if error.get('attr') == 'line_item_product_id' and error.get('detail') == 'This field cannot be updated after creation.':
                found_line_item_error = True
                break
        self.assertTrue(found_line_item_error, f"'line_item_product_id' error not found in {response.data['errors']}")

        item1.refresh_from_db()
        self.assertEqual(item1.line_item_product_id, initial_line_item_product_id)
        self.assertEqual(item1.quantity, initial_quantity) # Assert quantity did NOT update

    def test_update_bom_line_item_missing_quantity(self):
        """
        Tests attempting to update a BOM line item with a missing quantity, expecting a 400 Bad Request.
        """
        item1 = ProductBoMLineItem.objects.create(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=2
        )

        url = reverse("product-bom-detail", args=[
            self.red_company.id,
            self.purple_paint.id,
            item1.id
        ])

        response = self.client.put(url, {
            "line_item_product_id": self.blue_paint.id
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(ProductBoMLineItem.objects.filter(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=2
        ).exists())

    def test_update_bom_line_item(self):
        """
        Tests successfully updating the quantity of a BOM line item.
        """
        item1 = ProductBoMLineItem.objects.create(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=2
        )

        url = reverse("product-bom-detail", args=[
            self.red_company.id,
            self.purple_paint.id,
            item1.id
        ])

        response = self.client.put(url, {
            "quantity": 1
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ProductBoMLineItem.objects.filter(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=1
        ).exists())

    def test_update_bom_line_item_other_company(self):
        """
        Tests attempting to update a BOM line item belonging to a different company, expecting a 403 Forbidden.
        """
        item1 = ProductBoMLineItem.objects.create(
            line_item_product=self.red_paint,
            parent_product=self.magenta_paint,
            quantity=2
        )

        url = reverse("product-bom-detail", args=[
            self.blue_company.id,
            self.magenta_paint.id,
            item1.id
        ])

        response = self.client.put(url, {
            "quantity": 1,
            "line_item_product_id": self.blue_paint.id
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(ProductBoMLineItem.objects.filter(
            line_item_product=self.blue_paint,
            parent_product=self.magenta_paint,
            quantity=1
        ).exists())
        self.assertTrue(ProductBoMLineItem.objects.filter(
            line_item_product=self.red_paint,
            parent_product=self.magenta_paint,
            quantity=2
        ).exists())

    def test_update_bom_line_item_other_company_crashtest(self):
        """
        Tests attempting to update a BOM line item not associated with the specified company ID, expecting a 404 Not Found.
        """
        item1 = ProductBoMLineItem.objects.create(
            line_item_product=self.red_paint,
            parent_product=self.magenta_paint,
            quantity=2
        )

        url = reverse("product-bom-detail", args=[
            self.red_company.id,
            self.magenta_paint.id,
            item1.id
        ])

        response = self.client.put(url, {
            "quantity": 1,
            "line_item_product_id": self.blue_paint.id
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(ProductBoMLineItem.objects.filter(
            line_item_product=self.blue_paint,
            parent_product=self.magenta_paint,
            quantity=1
        ).exists())
        self.assertTrue(ProductBoMLineItem.objects.filter(
            line_item_product=self.red_paint,
            parent_product=self.magenta_paint,
            quantity=2
        ).exists())

    def test_partial_update_bom_line_item(self):
        """
        Tests attempting to partially update a BOM line item by changing its line item product ID, which should fail.
        """
        item1 = ProductBoMLineItem.objects.create(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=2
        )
        initial_line_item_product_id = item1.line_item_product_id
        initial_quantity = item1.quantity

        url = reverse("product-bom-detail", args=[
            self.red_company.id,
            self.purple_paint.id,
            item1.id
        ])

        response = self.client.patch(url, {
            "quantity": 1,
            "line_item_product_id": self.blue_paint.id
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data)
        found_line_item_error = False
        for error in response.data['errors']:
            if error.get('attr') == 'line_item_product_id' and error.get('detail') == 'This field cannot be updated after creation.':
                found_line_item_error = True
                break
        self.assertTrue(found_line_item_error, f"'line_item_product_id' error not found in {response.data['errors']}")

        item1.refresh_from_db()
        self.assertEqual(item1.line_item_product_id, initial_line_item_product_id)
        self.assertEqual(item1.quantity, initial_quantity)

    def test_partial_update_bom_line_item_quantity_only(self):
        """
        Tests successfully performing a partial update on a BOM line item's quantity.
        """
        item1 = ProductBoMLineItem.objects.create(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=1
        )

        url = reverse("product-bom-detail", args=[
            self.red_company.id,
            self.purple_paint.id,
            item1.id
        ])

        response = self.client.patch(url, {
            "quantity": 2
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ProductBoMLineItem.objects.filter(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=2
        ).exists())
        self.assertFalse(ProductBoMLineItem.objects.filter(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=1
        ).exists())

    def test_partial_update_bom_line_item_line_item_product_id_only(self):
        """
        Tests attempting to partially update a BOM line item by only changing its line item product ID, which should fail.
        """
        item1 = ProductBoMLineItem.objects.create(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=2
        )
        initial_line_item_product_id = item1.line_item_product_id
        initial_quantity = item1.quantity

        url = reverse("product-bom-detail", args=[
            self.red_company.id,
            self.purple_paint.id,
            item1.id
        ])

        response = self.client.patch(url, {
            "line_item_product_id": self.blue_paint.id
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data)
        found_line_item_error = False
        for error in response.data['errors']:
            if error.get('attr') == 'line_item_product_id' and error.get('detail') == 'This field cannot be updated after creation.':
                found_line_item_error = True
                break
        self.assertTrue(found_line_item_error, f"'line_item_product_id' error not found in {response.data['errors']}")

        item1.refresh_from_db()
        self.assertEqual(item1.line_item_product_id, initial_line_item_product_id)
        self.assertEqual(item1.quantity, initial_quantity)

    def test_partial_update_bom_line_item_other_company(self):
        """
        Tests attempting to partially update a BOM line item belonging to a different company, expecting a 403 Forbidden.
        """
        item1 = ProductBoMLineItem.objects.create(
            line_item_product=self.red_paint,
            parent_product=self.magenta_paint,
            quantity=2
        )

        url = reverse("product-bom-detail", args=[
            self.blue_company.id,
            self.magenta_paint.id,
            item1.id
        ])

        response = self.client.patch(url, {
            "quantity": 1,
            "line_item_product_id": self.blue_paint.id
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(ProductBoMLineItem.objects.filter(
            line_item_product=self.blue_paint,
            parent_product=self.magenta_paint,
            quantity=1
        ).exists())
        self.assertTrue(ProductBoMLineItem.objects.filter(
            line_item_product=self.red_paint,
            parent_product=self.magenta_paint,
            quantity=2
        ).exists())

    def test_partial_update_bom_line_item_other_company_crashtest(self):
        """
        Tests attempting to partially update a BOM line item not associated with the specified company ID, expecting a 404 Not Found.
        """
        item1 = ProductBoMLineItem.objects.create(
            line_item_product=self.red_paint,
            parent_product=self.magenta_paint,
            quantity=2
        )

        url = reverse("product-bom-detail", args=[
            self.red_company.id,
            self.magenta_paint.id,
            item1.id
        ])

        response = self.client.patch(url, {
            "quantity": 1,
            "line_item_product_id": self.blue_paint.id
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(ProductBoMLineItem.objects.filter(
            line_item_product=self.blue_paint,
            parent_product=self.magenta_paint,
            quantity=1
        ).exists())
        self.assertTrue(ProductBoMLineItem.objects.filter(
            line_item_product=self.red_paint,
            parent_product=self.magenta_paint,
            quantity=2
        ).exists())

    def test_partial_update_bom_empty_req(self):
        """
        Tests performing a partial update on a BOM line item with an empty request, expecting no changes.
        """
        item1 = ProductBoMLineItem.objects.create(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=2
        )

        url = reverse("product-bom-detail", args=[
            self.red_company.id,
            self.purple_paint.id,
            item1.id
        ])

        response = self.client.patch(url, {
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ProductBoMLineItem.objects.filter(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=2
        ).exists())

    def test_delete_bom_line_item(self):
        """
        Tests successfully deleting a BOM line item.
        """
        item1 = ProductBoMLineItem.objects.create(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=1
        )

        url = reverse("product-bom-detail", args=[
            self.red_company.id,
            self.purple_paint.id,
            item1.id
        ])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ProductBoMLineItem.objects.filter(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=1
        ).exists())

    def test_delete_bom_line_item_other_company(self):
        """
        Tests attempting to delete a BOM line item belonging to a different company, expecting a 403 Forbidden.
        """
        item1 = ProductBoMLineItem.objects.create(
            line_item_product=self.red_paint,
            parent_product=self.magenta_paint,
            quantity=1
        )

        url = reverse("product-bom-detail", args=[
            self.blue_company.id,
            self.magenta_paint.id,
            item1.id
        ])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(ProductBoMLineItem.objects.filter(
            line_item_product=self.red_paint,
            parent_product=self.magenta_paint,
            quantity=1
        ).exists())

    def test_delete_bom_line_item_other_company_crashtest(self):
        """
        Tests attempting to delete a BOM line item not associated with the specified company ID, expecting a 404 Not Found.
        """
        item1 = ProductBoMLineItem.objects.create(
            line_item_product=self.red_paint,
            parent_product=self.magenta_paint,
            quantity=1
        )

        url = reverse("product-bom-detail", args=[
            self.red_company.id,
            self.magenta_paint.id,
            item1.id
        ])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(ProductBoMLineItem.objects.filter(
            line_item_product=self.red_paint,
            parent_product=self.magenta_paint,
            quantity=1
        ).exists())

    def test_create_bom_line_item_duplicate(self):
        """
        Tests attempting to create a duplicate BOM line item, expecting a 400 Bad Request.
        """
        url = reverse("product-bom-list", args=[self.red_company.id, self.purple_paint.id])
        response = self.client.post(url, {
            "quantity": 1,
            "line_item_product_id": self.red_paint.id
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ProductBoMLineItem.objects.filter(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=1
        ).exists())

        response = self.client.post(url, {
            "quantity": 1,
            "line_item_product_id": self.red_paint.id
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ProductBoMLineItem.objects.filter(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=1
        ).count(),1)

    def test_create_bom_line_item_recursive_error(self):
        """
        Tests attempting to create a recursive BOM line item, expecting a 400 Bad Request.
        """
        url = reverse("product-bom-list", args=[self.red_company.id, self.purple_paint.id])
        response = self.client.post(url, {
            "quantity": 1,
            "line_item_product_id": self.red_paint.id
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ProductBoMLineItem.objects.filter(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=1
        ).exists())

        url = reverse("product-bom-list", args=[self.red_company.id, self.red_paint.id])
        response = self.client.post(url, {
            "quantity": 1,
            "line_item_product_id": self.purple_paint.id
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(ProductBoMLineItem.objects.filter(
            line_item_product=self.purple_paint,
            parent_product=self.red_paint,
            quantity=1
        ).exists())

    def test_create_bom_line_item_recursive_self_error(self):
        """
        Tests attempting to create a BOM line item where the product is its own component, expecting a 400 Bad Request.
        """
        url = reverse("product-bom-list", args=[self.red_company.id, self.red_paint.id])
        response = self.client.post(url, {
            "quantity": 1,
            "line_item_product_id": self.red_paint.id
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(ProductBoMLineItem.objects.filter(
            line_item_product=self.red_paint,
            parent_product=self.red_paint,
            quantity=1
        ).exists())

    def test_successful_put_update_bom_line_item_quantity(self):
        """
        Tests successfully updating a BOM line item's quantity using a PUT request.
        """
        item = ProductBoMLineItem.objects.create(
            line_item_product=self.red_paint, # Belongs to red_company
            parent_product=self.purple_paint, # Belongs to red_company
            quantity=2
        )
        initial_line_item_product_id = item.line_item_product_id
        initial_quantity = item.quantity

        url = reverse("product-bom-detail", args=[
            self.red_company.id,
            self.purple_paint.id,
            item.id
        ])

        new_quantity = initial_quantity + 5

        data = {
            "quantity": new_quantity
        }

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK, f"PUT failed with status {response.status_code}: {response.data}")

        item.refresh_from_db()

        self.assertEqual(item.quantity, new_quantity)
        self.assertEqual(item.line_item_product_id, initial_line_item_product_id)

    def test_successful_patch_update_bom_line_item_quantity(self):
        """
        Tests successfully updating a BOM line item's quantity using a PATCH request.
        """
        item = ProductBoMLineItem.objects.create(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=10
        )
        initial_line_item_product_id = item.line_item_product_id
        initial_quantity = item.quantity

        url = reverse("product-bom-detail", args=[
            self.red_company.id,
            self.purple_paint.id,
            item.id
        ])

        new_quantity = initial_quantity - 3

        data = {
            "quantity": new_quantity
        }

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK, f"PATCH failed with status {response.status_code}: {response.data}")

        item.refresh_from_db()

        self.assertEqual(item.quantity, new_quantity)
        self.assertEqual(item.line_item_product_id, initial_line_item_product_id)

    def test_create_bom_line_item_without_line_item_product_id(self):
        """
        Tests attempting to create a BOM line item without specifying a line item product ID.
        """
        url = reverse("product-bom-list", args=[self.red_company.id, self.purple_paint.id])
        data = {
            "quantity": 3
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data)
        found_line_item_error = False
        for error in response.data['errors']:
            if error.get('attr') == 'line_item_product' and error.get('detail') == 'This field is required.':
                found_line_item_error = True
                break
        self.assertTrue(found_line_item_error, f"'line_item_product' required error not found in {response.data['errors']}")

    def test_successful_create_bom_line_item(self):
        """
        Tests successfully creating a new BOM line item.
        """
        url = reverse("product-bom-list", args=[self.red_company.id, self.purple_paint.id])
        data = {
            "quantity": 5,
            "line_item_product_id": self.blue_paint.id
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['quantity'], 5)
        self.assertEqual(response.data['line_item_product']['id'], self.blue_paint.id)

        self.assertTrue(ProductBoMLineItem.objects.filter(
            parent_product=self.purple_paint,
            line_item_product=self.blue_paint,
            quantity=5
        ).exists())