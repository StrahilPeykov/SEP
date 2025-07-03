"""
Tests for the file exports API
"""

from io import BytesIO, TextIOWrapper

from aas_test_engines.file import *
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Product, ProductionEnergyEmission, UserEnergyEmission, TransportEmission
from core.tests.setup_functions import tech_companies_setup


class AASExportImportTests(APITestCase):
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

    def test_export_import_json(self):
        """
        Test for exporting product data in JSON format and re-importing it back in.
        """

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

        # Count the number of production energy/user energy/transport emissions in the original product
        production_energy_emissions = ProductionEnergyEmission.objects.filter(parent_product=self.iphone).count()
        user_energy_emissions = UserEnergyEmission.objects.filter(parent_product=self.iphone).count()
        transport_emissions = TransportEmission.objects.filter(parent_product=self.iphone).count()

        # Delete the product to simulate re-import and avoid conflicts
        self.iphone.delete()

        # Re-import the product
        import_url = reverse("product-import-aas-json", args=[self.apple.id])
        uploaded = SimpleUploadedFile("aas.json", buffer.getvalue(), content_type="application/json")
        import_response = self.client.post(import_url, {"file": uploaded}, format="multipart")
        self.assertEqual(import_response.status_code, status.HTTP_201_CREATED)

        # Check if the product was re-imported correctly
        reimported_product = Product.objects.get(id=import_response.data['id'])
        self.assertEqual(reimported_product.name, self.iphone.name)

        # Check if the emissions are also re-imported correctly
        self.assertEqual(
            ProductionEnergyEmission.objects.filter(parent_product=reimported_product).count(),
            production_energy_emissions
        )
        self.assertEqual(
            UserEnergyEmission.objects.filter(parent_product=reimported_product).count(),
            user_energy_emissions
        )
        self.assertEqual(
            TransportEmission.objects.filter(parent_product=reimported_product).count(),
            transport_emissions
        )

    def test_export_json_shared_product(self):
        """
        Test for exporting product data of another company that is shared with the user's company in JSON format.
        """

        url = reverse("product-export-aas-json", args=[self.samsung.id, self.camera.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_export_json_sharing_request_rejected(self):
        """
        Test for exporting product data of another company that is rejected to share with the user's company in
         JSON format.
        """

        url = reverse("product-export-aas-json", args=[self.tsmc.id, self.processor.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_export_json_sharing_request_not_requested(self):
        """
        Test for exporting product data of another company that is not requested by the user's company in JSON format.
        """

        url = reverse("product-export-aas-json", args=[self.samsung.id, self.flashlight.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_export_json_not_logged_in(self):
        """
        Test for exporting a product data from a company when not logged in for JSON export API.
        """

        self.access_token = ""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        url = reverse("product-export-aas-json", args=[self.apple.id, self.iphone.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_export_json_private_product(self):
        """
        Test for exporting a product data of a private product of another company for JSON API.
        """

        url = reverse("product-export-aas-json", args=[self.tsmc.id, self.quantum_pc.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_export_json_company_product_mismatch(self):
        """
        Test for trying to query the product of product that is not owned by that company for JSON export API.
        """

        url = reverse("product-export-aas-json", args=[self.apple.id, self.quantum_pc.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_export_import_xml(self):
        """
        Test for exporting a product data in XML format and re-importing it back in.
        """

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

        # Count the number of production energy/user energy/transport emissions in the original product
        production_energy_emissions = ProductionEnergyEmission.objects.filter(parent_product=self.iphone).count()
        user_energy_emissions = UserEnergyEmission.objects.filter(parent_product=self.iphone).count()
        transport_emissions = TransportEmission.objects.filter(parent_product=self.iphone).count()

        # Delete the product to simulate re-import and avoid conflicts
        self.iphone.delete()

        # Re-import the product
        import_url = reverse("product-import-aas-xml", args=[self.apple.id])
        uploaded = SimpleUploadedFile("aas.xml", buffer.getvalue(), content_type="application/xml")
        import_response = self.client.post(import_url, {"file": uploaded}, format="multipart")
        self.assertEqual(import_response.status_code, status.HTTP_201_CREATED)

        # Check if the product was re-imported correctly
        reimported_product = Product.objects.get(id=import_response.data['id'])
        self.assertEqual(reimported_product.name, self.iphone.name)

        # Check if the emissions are also re-imported correctly
        self.assertEqual(
            ProductionEnergyEmission.objects.filter(parent_product=reimported_product).count(),
            production_energy_emissions
        )
        self.assertEqual(
            UserEnergyEmission.objects.filter(parent_product=reimported_product).count(),
            user_energy_emissions
        )
        self.assertEqual(
            TransportEmission.objects.filter(parent_product=reimported_product).count(),
            transport_emissions
        )

    def test_export_xml_shared_product(self):
        """
        Test for exporting product data of another company that is shared with the user's company in XML format.
        """

        url = reverse("product-export-aas-xml", args=[self.samsung.id, self.camera.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_export_xml_sharing_request_rejected(self):
        """
        Test for exporting product data of another company that is rejected to share with the user's company in
         XML format.
        """

        url = reverse("product-export-aas-xml", args=[self.tsmc.id, self.processor.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_export_xml_sharing_request_not_requested(self):
        """
        Test for exporting product data of another company that is not requested by the user's company in XML format.
        """

        url = reverse("product-export-aas-xml", args=[self.samsung.id, self.flashlight.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_export_xml_not_logged_in(self):
        """
        Test for exporting a product data from a company when not logged in for XML export API.
        """

        self.access_token = ""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        url = reverse("product-export-aas-xml", args=[self.apple.id, self.iphone.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_export_xml_private_product(self):
        """
        Test for exporting a product data of a private product of another company for XML API.
        """

        url = reverse("product-export-aas-xml", args=[self.tsmc.id, self.quantum_pc.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_export_xml_company_product_mismatch(self):
        """
        Test for trying to query the product of product that is not owned by that company for XML export API.
        """

        url = reverse("product-export-aas-xml", args=[self.apple.id, self.quantum_pc.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_export_import_aasx(self):
        """
        Test for exporting a product data in AASX format and re-importing it back in.
        """

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


        # Count the number of production energy/user energy/transport emissions in the original product
        production_energy_emissions = ProductionEnergyEmission.objects.filter(parent_product=self.iphone).count()
        user_energy_emissions = UserEnergyEmission.objects.filter(parent_product=self.iphone).count()
        transport_emissions = TransportEmission.objects.filter(parent_product=self.iphone).count()

        # Delete the product to simulate re-import and avoid conflicts
        self.iphone.delete()

        # Re-import the product
        import_url = reverse("product-import-aas-aasx", args=[self.apple.id])
        uploaded = SimpleUploadedFile("aas.aasx", buffer.getvalue(),
                                      content_type="application/asset-administration-shell-package")
        import_response = self.client.post(import_url, {"file": uploaded}, format="multipart")
        self.assertEqual(import_response.status_code, status.HTTP_201_CREATED)

        # Check if the product was re-imported correctly
        reimported_product = Product.objects.get(id=import_response.data['id'])
        self.assertEqual(reimported_product.name, self.iphone.name)

        # Check if the emissions are also re-imported correctly
        self.assertEqual(
            ProductionEnergyEmission.objects.filter(parent_product=reimported_product).count(),
            production_energy_emissions
        )
        self.assertEqual(
            UserEnergyEmission.objects.filter(parent_product=reimported_product).count(),
            user_energy_emissions
        )
        self.assertEqual(
            TransportEmission.objects.filter(parent_product=reimported_product).count(),
            transport_emissions
        )

    def test_export_aasx_other_shared_product(self):
        """
        Test for exporting product data of another company that is shared with the user's company in AASX format.
        """

        url = reverse("product-export-aas-aasx", args=[self.samsung.id, self.camera.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_export_aasx_other_sharing_request_rejected(self):
        """
        Test for exporting product data of another company that is rejected to share with the user's company in
         AASX format.
        """

        url = reverse("product-export-aas-aasx", args=[self.tsmc.id, self.processor.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_export_aasx_other_sharing_request_not_requested(self):
        """
        Test for exporting product data of another company that is not requested by the user's company in AASX format.
        """

        url = reverse("product-export-aas-aasx", args=[self.samsung.id, self.flashlight.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_export_aasx_not_logged_in(self):
        """
        Test for exporting a product data from a company when not logged in for AASX export API.
        """

        self.access_token = ""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        url = reverse("product-export-aas-aasx", args=[self.apple.id, self.iphone.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_export_aasx_private_product(self):
        """
        Test for exporting a product data of a private product of another company for AASX API.
        """

        url = reverse("product-export-aas-aasx", args=[self.tsmc.id, self.quantum_pc.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_export_aasx_company_product_mismatch(self):
        """
        Test for trying to query the product of product that is not owned by that company for AASX export API.
        """

        url = reverse("product-export-aas-aasx", args=[self.apple.id, self.quantum_pc.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)