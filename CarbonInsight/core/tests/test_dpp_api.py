from io import BytesIO, TextIOWrapper

from aas_test_engines.file import *
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Product
from core.tests.setup_functions import tech_companies_setup


class DPPAPITests(APITestCase):
    def setUp(self):
        tech_companies_setup(self)

        self.quantum_pc = Product.objects.create(
            name="Quantum_pc",
            description="whoah",
            supplier=self.tsmc,
            manufacturer_name="TSMC",
            manufacturer_country="TW",
            manufacturer_city="Taiwan",
            manufacturer_street="Chua",
            manufacturer_zip_code="3816RTB",
            year_of_construction=2025,
            family="PC",
            sku="47398494875",
            is_public = False
        )
        self.flashlight = Product.objects.create(
            name="Flashlight",
            description="Flashlight",
            supplier=self.samsung,
            manufacturer_name="Samsung",
            manufacturer_country="KR",
            manufacturer_city="Seul",
            manufacturer_street="Hoinua",
            manufacturer_zip_code="31PTTK",
            year_of_construction=2025,
            family="Light Source",
            sku="3472384759334",
        )

    def test_export_json(self):
        url = reverse("product-export-aas-json", args=[self.apple.id, self.iphone.id])
        response = self.client.get(url)

        buffer = BytesIO()
        for chunk in response.streaming_content:
            buffer.write(chunk)
        buffer.name = 'downloaded_file.json'
        buffer.seek(0)

        text_buffer = TextIOWrapper(buffer)

        # Check file
        result = check_json_file(text_buffer)
        result.dump()
        self.assertTrue(result.ok())

    def test_export_json_shared_product(self):
        url = reverse("product-export-aas-json", args=[self.samsung.id, self.camera.id])
        response = self.client.get(url)

        buffer = BytesIO()
        for chunk in response.streaming_content:
            buffer.write(chunk)
        buffer.name = 'downloaded_file.json'
        buffer.seek(0)

        text_buffer = TextIOWrapper(buffer)

        # Check file
        result = check_json_file(text_buffer)
        result.dump()
        self.assertTrue(result.ok())

    def test_export_json_sharing_request_rejected(self):
        url = reverse("product-export-aas-json", args=[self.tsmc.id, self.processor.id])
        response = self.client.get(url)

        buffer = BytesIO()
        for chunk in response.streaming_content:
            buffer.write(chunk)
        buffer.name = 'downloaded_file.json'
        buffer.seek(0)

        text_buffer = TextIOWrapper(buffer)

        # Check file
        result = check_json_file(text_buffer)
        result.dump()
        self.assertTrue(result.ok())

    def test_export_json_sharing_request_not_requested(self):
        url = reverse("product-export-aas-json", args=[self.samsung.id, self.flashlight.id])
        response = self.client.get(url)

        buffer = BytesIO()
        for chunk in response.streaming_content:
            buffer.write(chunk)
        buffer.name = 'downloaded_file.json'
        buffer.seek(0)

        text_buffer = TextIOWrapper(buffer)

        # Check file
        result = check_json_file(text_buffer)
        result.dump()
        self.assertTrue(result.ok())

    def test_export_json_not_logged_in(self):
        self.access_token = ""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        url = reverse("product-export-aas-json", args=[self.apple.id, self.iphone.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_export_json_private_product(self):
        url = reverse("product-export-aas-json", args=[self.tsmc.id, self.quantum_pc.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_export_json_company_product_mismatch(self):
        url = reverse("product-export-aas-json", args=[self.apple.id, self.quantum_pc.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_export_xml(self):
        url = reverse("product-export-aas-xml", args=[self.apple.id, self.iphone.id])
        response = self.client.get(url)

        buffer = BytesIO()
        for chunk in response.streaming_content:
            buffer.write(chunk)
        buffer.name = 'downloaded_file.xml'
        buffer.seek(0)

        text_buffer = TextIOWrapper(buffer)

        # Check file
        result = check_xml_file(text_buffer)
        result.dump()
        self.assertTrue(result.ok())

    def test_export_xml_shared_product(self):
        url = reverse("product-export-aas-xml", args=[self.samsung.id, self.camera.id])
        response = self.client.get(url)

        buffer = BytesIO()
        for chunk in response.streaming_content:
            buffer.write(chunk)
        buffer.name = 'downloaded_file.xml'
        buffer.seek(0)

        text_buffer = TextIOWrapper(buffer)

        # Check file
        result = check_xml_file(text_buffer)
        result.dump()
        self.assertTrue(result.ok())

    def test_export_xml_sharing_request_rejected(self):
        url = reverse("product-export-aas-xml", args=[self.tsmc.id, self.processor.id])
        response = self.client.get(url)

        buffer = BytesIO()
        for chunk in response.streaming_content:
            buffer.write(chunk)
        buffer.name = 'downloaded_file.xml'
        buffer.seek(0)

        text_buffer = TextIOWrapper(buffer)

        # Check file
        result = check_xml_file(text_buffer)
        result.dump()
        self.assertTrue(result.ok())

    def test_export_xml_sharing_request_not_requested(self):
        url = reverse("product-export-aas-xml", args=[self.samsung.id, self.flashlight.id])
        response = self.client.get(url)

        buffer = BytesIO()
        for chunk in response.streaming_content:
            buffer.write(chunk)
        buffer.name = 'downloaded_file.xml'
        buffer.seek(0)

        text_buffer = TextIOWrapper(buffer)

        # Check file
        result = check_xml_file(text_buffer)
        result.dump()
        self.assertTrue(result.ok())

    def test_export_xml_not_logged_in(self):
        self.access_token = ""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        url = reverse("product-export-aas-xml", args=[self.apple.id, self.iphone.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_export_xml_private_product(self):
        url = reverse("product-export-aas-xml", args=[self.tsmc.id, self.quantum_pc.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_export_xml_company_product_mismatch(self):
        url = reverse("product-export-aas-xml", args=[self.apple.id, self.quantum_pc.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_export_aasx(self):
        url = reverse("product-export-aas-aasx", args=[self.apple.id, self.iphone.id])
        response = self.client.get(url)

        buffer = BytesIO()
        for chunk in response.streaming_content:
            buffer.write(chunk)
        buffer.name = 'downloaded_file.xml'
        buffer.seek(0)

        # Check file
        result = check_aasx_file(buffer)
        result.dump()
        self.assertTrue(result.ok())

    def test_export_aasx_other_shared_product(self):
        url = reverse("product-export-aas-aasx", args=[self.samsung.id, self.camera.id])
        response = self.client.get(url)

        buffer = BytesIO()
        for chunk in response.streaming_content:
            buffer.write(chunk)
        buffer.name = 'downloaded_file.xml'
        buffer.seek(0)

        # Check file
        result = check_aasx_file(buffer)
        result.dump()
        self.assertTrue(result.ok())

    def test_export_aasx_other_sharing_request_rejected(self):
        url = reverse("product-export-aas-aasx", args=[self.tsmc.id, self.processor.id])
        response = self.client.get(url)

        buffer = BytesIO()
        for chunk in response.streaming_content:
            buffer.write(chunk)
        buffer.name = 'downloaded_file.xml'
        buffer.seek(0)

        # Check file
        result = check_aasx_file(buffer)
        result.dump()
        self.assertTrue(result.ok())

    def test_export_aasx_other_sharing_request_not_requested(self):
        url = reverse("product-export-aas-aasx", args=[self.samsung.id, self.flashlight.id])
        response = self.client.get(url)

        buffer = BytesIO()
        for chunk in response.streaming_content:
            buffer.write(chunk)
        buffer.name = 'downloaded_file.xml'
        buffer.seek(0)

        # Check file
        result = check_aasx_file(buffer)
        result.dump()
        self.assertTrue(result.ok())

    def test_export_aasx_not_logged_in(self):
        self.access_token = ""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        url = reverse("product-export-aas-aasx", args=[self.apple.id, self.iphone.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_export_aasx_private_product(self):
        url = reverse("product-export-aas-aasx", args=[self.tsmc.id, self.quantum_pc.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_export_aasx_company_product_mismatch(self):
        url = reverse("product-export-aas-aasx", args=[self.apple.id, self.quantum_pc.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)