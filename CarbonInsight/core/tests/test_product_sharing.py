from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from core.models import CompanyMembership, Product, ProductSharingRequest, ProductSharingRequestStatus
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

    def test_request_product_sharing_own_company_product(self):
        url = reverse("product-request-access", args=[self.red_company.id, self.red_paint.id])
        response = self.client.post(url, {"requester":self.red_company.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(ProductSharingRequest.objects.filter(
            product = self.red_paint,
            requester=self.red_company).exists())

    def test_request_product_sharing_own_company_private_product(self):
        url = reverse("product-request-access", args=[self.red_company.id, self.red_secret_plans.id])
        response = self.client.post(url, {"requester":self.red_company.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(ProductSharingRequest.objects.filter(
            product = self.red_secret_plans,
            requester=self.red_company).exists())

    def test_request_product_sharing_other_company_product(self):
        url = reverse("product-request-access", args=[self.blue_company.id, self.blue_paint.id])
        response = self.client.post(url, {"requester":self.red_company.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ProductSharingRequest.objects.filter(
            product = self.blue_paint,
            requester=self.red_company).exists())

    def test_request_product_sharing_other_company_private_product(self):
        url = reverse("product-request-access", args=[self.blue_company.id, self.blue_secret_plans.id])
        response = self.client.post(url, {"requester":self.red_company.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(ProductSharingRequest.objects.filter(
            product = self.blue_secret_plans,
            requester=self.red_company).exists())

    def test_request_product_sharing_other_company_product_multiple_attempts(self):
        url = reverse("product-request-access", args=[self.blue_company.id, self.blue_paint.id])
        response = self.client.post(url, {"requester":self.red_company.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ProductSharingRequest.objects.filter(
            product = self.blue_paint,
            requester=self.red_company).exists())

        url = reverse("product-request-access", args=[self.blue_company.id, self.blue_paint.id])
        response = self.client.post(url, {"requester": self.red_company.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ProductSharingRequest.objects.filter(
            product=self.blue_paint,
            requester=self.red_company).exists())

    def test_product_sharing_request_list(self):
        url = reverse("product_sharing_requests-list", args=[self.red_company.id])

        ProductSharingRequest.objects.create(
            product=self.red_paint,
            requester=self.blue_company,
            status = ProductSharingRequestStatus.PENDING
        )

        ProductSharingRequest.objects.create(
            product=self.purple_paint,
            requester=self.blue_company,
            status=ProductSharingRequestStatus.PENDING
        )

        response = self.client.get(url, format="json")

        requested_products = [product["product_name"] for product in response.data]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Red paint", requested_products)
        self.assertIn("Purple paint", requested_products)

    def test_accept_single_product_sharing_request(self):
        url = reverse("product_sharing_requests-bulk-approve", args=[self.red_company.id])

        psr_1 = ProductSharingRequest.objects.create(
            product=self.red_paint,
            requester=self.blue_company,
            status = ProductSharingRequestStatus.PENDING
        )

        ProductSharingRequest.objects.create(
            product=self.purple_paint,
            requester=self.blue_company,
            status=ProductSharingRequestStatus.PENDING
        )

        response = self.client.post(url,{"ids":[psr_1.id]}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ProductSharingRequest.objects.filter(
            product=self.red_paint,
            status=ProductSharingRequestStatus.ACCEPTED
        ).exists())
        self.assertTrue(ProductSharingRequest.objects.filter(
            product=self.purple_paint,
            status=ProductSharingRequestStatus.PENDING
        ).exists())

    def test_accept_multiple_product_sharing_request(self):
        url = reverse("product_sharing_requests-bulk-approve", args=[self.red_company.id])

        psr_1 = ProductSharingRequest.objects.create(
            product=self.red_paint,
            requester=self.blue_company,
            status = ProductSharingRequestStatus.PENDING
        )

        psr_2 = ProductSharingRequest.objects.create(
            product=self.purple_paint,
            requester=self.blue_company,
            status=ProductSharingRequestStatus.PENDING
        )

        response = self.client.post(url,{"ids":[psr_1.id, psr_2.id]}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ProductSharingRequest.objects.filter(
            product=self.red_paint,
            status=ProductSharingRequestStatus.ACCEPTED
        ).exists())
        self.assertTrue(ProductSharingRequest.objects.filter(
            product=self.purple_paint,
            status=ProductSharingRequestStatus.ACCEPTED
        ).exists())

    def test_reject_single_product_sharing_request(self):
        url = reverse("product_sharing_requests-bulk-deny", args=[self.red_company.id])

        psr_1 = ProductSharingRequest.objects.create(
            product=self.red_paint,
            requester=self.blue_company,
            status = ProductSharingRequestStatus.PENDING
        )

        ProductSharingRequest.objects.create(
            product=self.purple_paint,
            requester=self.blue_company,
            status=ProductSharingRequestStatus.PENDING
        )

        response = self.client.post(url,{"ids":[psr_1.id]}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ProductSharingRequest.objects.filter(
            product=self.red_paint,
            status=ProductSharingRequestStatus.REJECTED
        ).exists())
        self.assertTrue(ProductSharingRequest.objects.filter(
            product=self.purple_paint,
            status=ProductSharingRequestStatus.PENDING
        ).exists())

    def test_reject_multiple_product_sharing_request(self):
        url = reverse("product_sharing_requests-bulk-deny", args=[self.red_company.id])

        psr_1 = ProductSharingRequest.objects.create(
            product=self.red_paint,
            requester=self.blue_company,
            status = ProductSharingRequestStatus.PENDING
        )

        psr_2 = ProductSharingRequest.objects.create(
            product=self.purple_paint,
            requester=self.blue_company,
            status=ProductSharingRequestStatus.PENDING
        )

        response = self.client.post(url,{"ids":[psr_1.id, psr_2.id]}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ProductSharingRequest.objects.filter(
            product=self.red_paint,
            status=ProductSharingRequestStatus.REJECTED
        ).exists())
        self.assertTrue(ProductSharingRequest.objects.filter(
            product=self.purple_paint,
            status=ProductSharingRequestStatus.REJECTED
        ).exists())