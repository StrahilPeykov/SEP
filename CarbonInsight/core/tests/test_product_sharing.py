from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from core.models import CompanyMembership, Product, ProductSharingRequest, ProductSharingRequestStatus
from core.models.company import Company
from core.tests.setup_functions import paint_companies_setup

User = get_user_model()

class ProductAPITest(APITestCase):
    def setUp(self):
        paint_companies_setup(self)

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