from io import BytesIO
import zipfile

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.exporters.zip import product_to_zip
from core.tests.setup_functions import tech_companies_setup


class ZipExporterTests(APITestCase):
    def setUp(self):
        tech_companies_setup(self)

    def test_zip_contains_all_expected_files(self):
        """
        Ensure that the ZIP archive for a product contains all expected files and they are non-empty.
        """
        # Use the iPhone product from the tech_companies_setup scenario
        product = self.iphone
        buf = product_to_zip(product)
        buf.seek(0)

        # Open the ZIP and inspect its contents
        with zipfile.ZipFile(buf) as zf:
            namelist = zf.namelist()

            expected_files = [
                f"{product.name}_aas.aasx",
                f"{product.name}_aas.json",
                f"{product.name}_aas.xml",
                f"{product.name}_scsn_full.xml",
                f"{product.name}_scsn_pcf.xml",
                f"{product.name}_transport_emissions.csv",
                f"{product.name}_user_energy_emissions.csv",
                f"{product.name}_production_energy_emissions.csv",
            ]

            # Check that all expected filenames are present
            for filename in expected_files:
                self.assertIn(filename, namelist, f"{filename} not found in ZIP contents")

            # Verify that each file has non-zero content
            for filename in expected_files:
                data = zf.read(filename)
                self.assertTrue(data, f"{filename} is empty")

    def test_export_zip_view_success(self):
        """
        Authenticated member should be able to download ZIP via API endpoint.
        """
        url = reverse("product-export-zip", args=[self.apple.id, self.iphone.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/zip")
        cd = response["Content-Disposition"]
        self.assertIn(f"{self.iphone.name}.zip", cd)

        # Ensure response body is non-empty ZIP
        buf = BytesIO()
        for chunk in response.streaming_content:
            buf.write(chunk)
        buf.seek(0)
        with zipfile.ZipFile(buf) as zf:
            self.assertTrue(zf.namelist(), "ZIP from view is empty")

    def test_export_zip_view_unauthenticated(self):
        """
        Unauthenticated requests should be denied.
        """
        # Clear credentials
        self.client.credentials()
        url = reverse("product-export-zip", args=[self.apple.id, self.iphone.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_export_zip_view_not_member(self):
        """
        Authenticated non-member of the product's supplier company should be forbidden.
        """
        # Obtain token for a Samsung user (not member of Apple)
        token_url = reverse("token_obtain_pair")
        resp = self.client.post(
            token_url,
            {"username": "samsung1@samsung.com", "password": "1234567890"},
            format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        samsung_token = resp.data.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {samsung_token}")

        url = reverse("product-export-zip", args=[self.apple.id, self.iphone.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)