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

    def test_transport_emission_linked_to_other_product_bom_item_detail(self):
        bom_item_other = ProductBoMLineItem.objects.create(
            parent_product=self.red_paint,
            line_item_product=self.blue_paint,
            quantity=1
        )

        transport_emission_other_product = TransportEmission.objects.create(
            parent_product=self.purple_paint,
            distance=500.0,
            weight=100.0,
            reference=self.transport_ref_ship,
        )

        EmissionBoMLink.objects.create(
            emission=transport_emission_other_product,
            line_item=bom_item_other
        )

        url = reverse(
            "product-transport-emissions-detail",
            args=[self.red_company.id, self.purple_paint.id, transport_emission_other_product.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('line_items', response.data)
        self.assertIsInstance(response.data['line_items'], list)
        self.assertIn(bom_item_other.id, response.data['line_items'],
                      f"BOM item ID {bom_item_other.id} unexpectedly not found in transport emission's line_items: {response.data['line_items']}.")

    def test_transport_emission_linked_to_same_product_bom_item_detail(self):
        bom_item = ProductBoMLineItem.objects.create(
            parent_product=self.product_for_emission_linking_parent,
            line_item_product=self.product_for_emission_linking_child,
            quantity=1
        )

        transport_emission = TransportEmission.objects.create(
            parent_product=self.product_for_emission_linking_child,
            distance=200.0,
            weight=50.0,
            reference=self.transport_ref_ship,
        )

        EmissionBoMLink.objects.create(
            emission=transport_emission,
            line_item=bom_item
        )

        url = reverse(
            "product-transport-emissions-detail",
            args=[self.red_company.id, self.product_for_emission_linking_child.id, transport_emission.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('line_items', response.data)
        self.assertIsInstance(response.data['line_items'], list)
        self.assertIn(bom_item.id, response.data['line_items'],
                      f"BOM item ID {bom_item.id} not in transport emission's line_items.")

    def test_user_energy_emission_linked_to_other_product_bom_item_id(self):
        bom_item_other = ProductBoMLineItem.objects.create(
            parent_product=self.red_paint,
            line_item_product=self.blue_paint,
            quantity=1
        )

        user_emission_other_product = UserEnergyEmission.objects.create(
            parent_product=self.purple_paint,
            energy_consumption=15.0,
            reference=self.user_energy_ref
        )

        EmissionBoMLink.objects.create(
            emission=user_emission_other_product,
            line_item=bom_item_other
        )

        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.purple_paint.id, user_emission_other_product.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('line_items', response.data)
        self.assertIsInstance(response.data['line_items'], list)
        self.assertIn(bom_item_other.id, response.data['line_items'],
                         f"BOM item ID {bom_item_other.id} unexpectedly not found in user emission's line_items: {response.data['line_items']}.")

    def test_user_energy_emission_linked_to_same_product_bom_item_id(self):

        bom_item = ProductBoMLineItem.objects.create(
            parent_product=self.product_for_emission_linking_parent,
            line_item_product=self.product_for_emission_linking_child,
            quantity=1
        )

        user_emission = UserEnergyEmission.objects.create(
            parent_product=self.product_for_emission_linking_child,
            energy_consumption=10.0,
            reference=self.user_energy_ref
        )

        EmissionBoMLink.objects.create(
            emission=user_emission,
            line_item=bom_item
        )

        url = reverse(
            "product-user-energy-emissions-detail",
            args=[self.red_company.id, self.product_for_emission_linking_child.id, user_emission.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('line_items', response.data)
        self.assertIsInstance(response.data['line_items'], list)
        self.assertIn(bom_item.id, response.data['line_items'],
                      f"BOM item ID {bom_item.id} not in user emission's line_items.")

    def test_production_energy_emission_linked_to_same_product_bom_item_id(self):

        bom_item = ProductBoMLineItem.objects.create(
            parent_product=self.product_for_emission_linking_parent,
            line_item_product=self.product_for_emission_linking_child,
            quantity=1
        )

        production_emission = ProductionEnergyEmission.objects.create(
            parent_product=self.product_for_emission_linking_child,
            energy_consumption=25.0,
            reference=self.production_energy_ref
        )

        EmissionBoMLink.objects.create(
            emission=production_emission,
            line_item=bom_item
        )

        url = reverse(
            "product-production-energy-emissions-detail",
            args=[self.red_company.id, self.product_for_emission_linking_child.id, production_emission.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('line_items', response.data)
        self.assertIsInstance(response.data['line_items'], list)
        self.assertIn(bom_item.id, response.data['line_items'],
                      f"BOM item ID {bom_item.id} not in production emission's line_items.")

    def test_production_energy_emission_linked_to_other_product_bom_item_id(self):

        blue_company_user = User.objects.create_user(
            username="blue@bluecompany.com", email="blue@bluecompany.com", password="passwordblue")
        CompanyMembership.objects.create(user=blue_company_user, company=self.blue_company)
        self.client.force_authenticate(user=blue_company_user)
        url_blue_token = reverse("token_obtain_pair")
        response_blue_token = self.client.post(
            url_blue_token,
            {"username": "blue@bluecompany.com", "password": "passwordblue"},
            format="json"
        )
        self.assertEqual(response_blue_token.status_code, status.HTTP_200_OK)
        access_token_blue = response_blue_token.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token_blue}")

        bom_item_other = ProductBoMLineItem.objects.create(
            parent_product=self.red_secret_plans,
            line_item_product=self.blue_secret_plans,
            quantity=1
        )

        production_emission_other_product = ProductionEnergyEmission.objects.create(
            parent_product=self.magenta_paint,
            energy_consumption=30.0,
            reference=self.production_energy_ref
        )

        EmissionBoMLink.objects.create(
            emission=production_emission_other_product,
            line_item=bom_item_other
        )

        url = reverse(
            "product-production-energy-emissions-detail",
            args=[self.blue_company.id, self.magenta_paint.id, production_emission_other_product.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('line_items', response.data)
        self.assertIsInstance(response.data['line_items'], list)
        self.assertIn(bom_item_other.id, response.data['line_items'],
                         f"BOM item ID {bom_item_other.id} unexpectedly not found in production emission's line_items: {response.data['line_items']}.")

    def test_get_product_list_bom(self):
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
        url = reverse("product-bom-detail", args=[
            self.red_company.id,
            self.purple_paint.id,
            1
        ])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_specific_product_bom_other_company(self):
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
        url = reverse("product-bom-list", args=[self.red_company.id, self.purple_paint.id])
        response = self.client.post(url, {
            "line_item_product_id": self.red_paint.id
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bom_line_item_missing_line_item_product_id(self):
        url = reverse("product-bom-list", args=[self.red_company.id, self.purple_paint.id])
        response = self.client.post(url, {
            "quantity": 1
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bom_line_item_other_company(self):
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