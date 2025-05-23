from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from core.models import CompanyMembership, Product, ProductBoMLineItem, \
    ProductionEnergyEmissionReference, EmissionBoMLink, ProductionEnergyEmission, UserEnergyEmissionReference, \
    UserEnergyEmission, MaterialEmissionReference, MaterialEmissionReferenceFactor, LifecycleStage, MaterialEmission
from core.models.company import Company

User = get_user_model()

class ProductAPITest(APITestCase):
    def setUp(self):

        #Create User
        self.red_company_user = User.objects.create_user(
            username="1@redcompany.com", email="1@redcompany.com", password="1234567890")

        #Obtain JWT for user
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url,
            {"username": "1@redcompany.com", "password": "1234567890"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.access_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        self.red_company = Company.objects.create(
            name="Red company BV",
            vat_number="VATRED",
            business_registration_number="NL123456"
        )

        self.blue_company = Company.objects.create(
            name="Blue company BV",
            vat_number="VATBLUE",
            business_registration_number="NL654321"
        )

        CompanyMembership.objects.create(user=self.red_company_user, company=self.red_company)

        self.red_paint = Product.objects.create(
            name="Red paint",
            description="Red paint",
            supplier=self.red_company,
            manufacturer_name="Red company",
            manufacturer_country="NL",
            manufacturer_city="Eindhoven",
            manufacturer_street="De Zaale",
            manufacturer_zip_code="5612AZ",
            year_of_construction=2025,
            family="Paint",
            sku="12345678999",
            is_public=True
        )

        self.purple_paint = Product.objects.create(
            name="Purple paint",
            description="Purple paint",
            supplier=self.red_company,
            manufacturer_name="Red company",
            manufacturer_country="NL",
            manufacturer_city="Eindhoven",
            manufacturer_street="De Zaale",
            manufacturer_zip_code="5612AZ",
            year_of_construction=2025,
            family="Paint",
            sku="12345678988",
            is_public=True
        )

        self.red_secret_plans = Product.objects.create(
            name="Secret Plan Red",
            description="Secret Plan Red",
            supplier=self.red_company,
            manufacturer_name="Red company",
            manufacturer_country="NL",
            manufacturer_city="Eindhoven",
            manufacturer_street="De Zaale",
            manufacturer_zip_code="5612AZ",
            year_of_construction=2025,
            family="Paint",
            sku="111222333444",
            is_public=False
        )

        self.blue_paint = Product.objects.create(
            name="Blue paint",
            description="Blue paint",
            supplier=self.blue_company,
            manufacturer_name="Blue company",
            manufacturer_country="NL",
            manufacturer_city="Eindhoven",
            manufacturer_street="De Zaale",
            manufacturer_zip_code="5612AZ",
            year_of_construction=2025,
            family="Paint",
            sku="12345678999",
            is_public=True
        )

        self.magenta_paint = Product.objects.create(
            name="Magenta paint",
            description="Magenta paint",
            supplier=self.blue_company,
            manufacturer_name="Blue company",
            manufacturer_country="NL",
            manufacturer_city="Eindhoven",
            manufacturer_street="De Zaale",
            manufacturer_zip_code="5612AZ",
            year_of_construction=2025,
            family="Paint",
            sku="12345678999",
            is_public=True
        )

        self.blue_secret_plans = Product.objects.create(
            name="Secret Plan Blue",
            description="Secret Plan Blue",
            supplier=self.blue_company,
            manufacturer_name="Blue company",
            manufacturer_country="NL",
            manufacturer_city="Eindhoven",
            manufacturer_street="De Zaale",
            manufacturer_zip_code="5612AZ",
            year_of_construction=2025,
            family="Paint",
            sku="111222333444",
            is_public=False
        )

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

        self.mat_ref_plastic_bom = MaterialEmissionReference.objects.create(
            common_name="Plastic for BOM"
        )

    def test_material_emission_linked_to_same_product_not_in_bom(self):
        material_emission_parent = MaterialEmission.objects.create(
            parent_product=self.product_for_emission_linking_parent,
            weight=1.5,
            reference=self.mat_ref_plastic_bom,
        )

        bom_url = reverse(
            "product-bom-list",
            args=[self.red_company.id, self.product_for_emission_linking_parent.id]
        )
        bom_response = self.client.get(bom_url)
        self.assertEqual(bom_response.status_code, status.HTTP_200_OK)

        found_emission_in_bom = False
        for item in bom_response.data:
            emissions = item.get('emissions', [])
            for emission in emissions:
                if emission.get('type') == "MaterialEmission" and emission.get('id') == material_emission_parent.id:
                    found_emission_in_bom = True
                    break
            if found_emission_in_bom:
                break
        self.assertFalse(found_emission_in_bom,
                         "MaterialEmission linked directly to the parent product should not be in BOM line items.")

    def test_material_emission_linked_to_other_product_bom_item_detail(self):
        bom_item_other = ProductBoMLineItem.objects.create(
            parent_product=self.red_paint,
            line_item_product=self.blue_paint,
            quantity=1
        )

        material_emission_other_product = MaterialEmission.objects.create(
            parent_product=self.purple_paint,
            weight=7.5,
            reference=self.mat_ref_plastic_bom,
        )

        EmissionBoMLink.objects.create(
            emission=material_emission_other_product,
            line_item=bom_item_other
        )

        url = reverse(
            "product-material-emissions-detail",
            args=[self.red_company.id, self.purple_paint.id, material_emission_other_product.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('line_items', response.data)
        self.assertIsInstance(response.data['line_items'], list)
        self.assertIn(bom_item_other.id, response.data['line_items'],
                      f"BOM item ID {bom_item_other.id} unexpectedly not found in material emission's line_items: {response.data['line_items']}.")

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
            self.red_company_user.id,
            self.purple_paint.id,
            item1.id
        ])

        url2 = reverse("product-bom-detail", args=[
            self.red_company_user.id,
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
            self.red_company_user.id,
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
            "quantity": 1,
            "line_item_product_id": self.blue_paint.id
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ProductBoMLineItem.objects.filter(
            line_item_product=self.blue_paint,
            parent_product=self.purple_paint,
            quantity=1
        ).exists())
        self.assertFalse(ProductBoMLineItem.objects.filter(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=2
        ).exists())

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

    def test_update_bom_line_item_missing_line_item_product_id(self):
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

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(ProductBoMLineItem.objects.filter(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=2
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

        url = reverse("product-bom-detail", args=[
            self.red_company.id,
            self.purple_paint.id,
            item1.id
        ])

        response = self.client.patch(url, {
            "quantity": 1,
            "line_item_product_id": self.blue_paint.id
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ProductBoMLineItem.objects.filter(
            line_item_product=self.blue_paint,
            parent_product=self.purple_paint,
            quantity=1
        ).exists())
        self.assertFalse(ProductBoMLineItem.objects.filter(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=2
        ).exists())

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

        url = reverse("product-bom-detail", args=[
            self.red_company.id,
            self.purple_paint.id,
            item1.id
        ])

        response = self.client.patch(url, {
            "line_item_product_id": self.blue_paint.id
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ProductBoMLineItem.objects.filter(
            line_item_product=self.blue_paint,
            parent_product=self.purple_paint,
            quantity=2
        ).exists())
        self.assertFalse(ProductBoMLineItem.objects.filter(
            line_item_product=self.red_paint,
            parent_product=self.purple_paint,
            quantity=2
        ).exists())

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