from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from core.models import CompanyMembership, Product,ProductBoMLineItem
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