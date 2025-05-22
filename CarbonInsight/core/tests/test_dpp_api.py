from io import BytesIO, TextIOWrapper

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import User, EmissionBoMLink, ProductBoMLineItem, Product, CompanyMembership, Company
from core.models import UserEnergyEmission, ProductionEnergyEmission, TransportEmission,MaterialEmission
from core.models import  UserEnergyEmissionReference, ProductionEnergyEmissionReference, TransportEmissionReference, \
    MaterialEmissionReference
from core.models import UserEnergyEmissionReferenceFactor, TransportEmissionReferenceFactor, \
    MaterialEmissionReferenceFactor, ProductionEnergyEmissionReferenceFactor , LifecycleStage
from core.models import ProductSharingRequestStatus, ProductSharingRequest
from core.models.product import ProductEmissionOverrideFactor
from core.models import EmissionOverrideFactor
from aas_test_engines.file import *

class DPPAPITests(APITestCase):
    def setUp(self):
        admin_user = User.objects.create_user(username="admin@example.com", email="admin@example.com",
                                              password="1234567890")
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.save()
        apple_user_1 = User.objects.create_user(username="apple1@apple.com", email="apple1@apple.com",
                                                password="1234567890")
        apple_user_2 = User.objects.create_user(username="apple2@apple.com", email="apple2@apple.com",
                                                password="1234567890")
        samsung_user_1 = User.objects.create_user(username="samsung1@samsung.com", email="samsung1@samsung.com",
                                                  password="1234567890")
        corning_user_1 = User.objects.create_user(username="corning1@corning.com", email="corning1@corning.com",
                                                  password="1234567890")
        tsmc_user_1 = User.objects.create_user(username="tsmc1@tsmc.com", email="tsmc1@tsmc.com", password="1234567890")

        # Obtain JWT for user
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url,
            {"username": "apple1@apple.com", "password": "1234567890"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.access_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        # Create test companies
        self.apple = Company.objects.create(
            name="Apple Inc.",
            vat_number="TEST123456",
            business_registration_number="REG123456"
        )
        self.samsung = Company.objects.create(
            name="Samsung Electronics",
            vat_number="TEST654321",
            business_registration_number="REG654321"
        )
        corning = Company.objects.create(
            name="Corning Inc.",
            vat_number="TEST789012",
            business_registration_number="REG789012"
        )
        self.tsmc = Company.objects.create(
            name="Taiwan Semiconductor Manufacturing Company",
            vat_number="TEST345678",
            business_registration_number="REG345678"
        )

        # Create company memberships
        CompanyMembership.objects.create(user=admin_user, company=self.apple)
        CompanyMembership.objects.create(user=admin_user, company=self.samsung)
        CompanyMembership.objects.create(user=admin_user, company=corning)
        CompanyMembership.objects.create(user=admin_user, company=self.tsmc)
        CompanyMembership.objects.create(user=apple_user_1, company=self.apple)
        CompanyMembership.objects.create(user=apple_user_2, company=self.apple)
        CompanyMembership.objects.create(user=samsung_user_1, company=self.samsung)
        CompanyMembership.objects.create(user=corning_user_1, company=corning)
        CompanyMembership.objects.create(user=tsmc_user_1, company=self.tsmc)

        # Add material emission references
        glass_material = MaterialEmissionReference.objects.create(common_name="Glass")
        MaterialEmissionReferenceFactor.objects.create(
            emission_reference=glass_material,
            lifecycle_stage=LifecycleStage.A1,
            co_2_emission_factor=0.5,
        )
        silicon_material = MaterialEmissionReference.objects.create(common_name="Silicon")
        MaterialEmissionReferenceFactor.objects.create(
            emission_reference=silicon_material,
            lifecycle_stage=LifecycleStage.A2,
            co_2_emission_factor=0.3,
        )
        MaterialEmissionReferenceFactor.objects.create(
            emission_reference=silicon_material,
            lifecycle_stage=LifecycleStage.A1,
            co_2_emission_factor=0.2,
        )

        # Add transport emission references
        transport_air = TransportEmissionReference.objects.create(common_name="Air transport")
        TransportEmissionReferenceFactor.objects.create(
            emission_reference=transport_air,
            lifecycle_stage=LifecycleStage.A3,
            co_2_emission_factor=0.2,
        )
        TransportEmissionReferenceFactor.objects.create(
            emission_reference=transport_air,
            lifecycle_stage=LifecycleStage.A4,
            co_2_emission_factor=0.3,
        )

        transport_road = TransportEmissionReference.objects.create(common_name="Road transport")
        TransportEmissionReferenceFactor.objects.create(
            emission_reference=transport_road,
            lifecycle_stage=LifecycleStage.A3,
            co_2_emission_factor=0.05,
        )

        # Add production energy emission references
        assembly_line_reference = ProductionEnergyEmissionReference.objects.create(common_name="Assembly line")
        ProductionEnergyEmissionReferenceFactor.objects.create(
            emission_reference=assembly_line_reference,
            lifecycle_stage=LifecycleStage.A3,
            co_2_emission_factor=0.4,
        )

        # Add user energy emission references
        charging_phone = UserEnergyEmissionReference.objects.create(common_name="Charging phone")
        UserEnergyEmissionReferenceFactor.objects.create(
            emission_reference=charging_phone,
            lifecycle_stage=LifecycleStage.A5,
            co_2_emission_factor=0.2,
        )
        update_processor = UserEnergyEmissionReference.objects.create(common_name="Update processor")
        UserEnergyEmissionReferenceFactor.objects.create(
            emission_reference=update_processor,
            lifecycle_stage=LifecycleStage.A5,
            co_2_emission_factor=0.2,
        )

        # Add products to companies
        self.processor = Product.objects.create(
            name="A14 processor",
            description="Main processor used in iPhones",
            supplier=self.tsmc,
            manufacturer_name="TSMC",
            manufacturer_country="TW",
            manufacturer_city="Taiwan",
            manufacturer_street="Chua",
            manufacturer_zip_code="3816RTB",
            year_of_construction=2025,
            family="Processor",
            sku="111222333444",
        )
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
        self.camera = Product.objects.create(
            name="Camera module",
            description="Camera module used in various phones",
            supplier=self.samsung,
            manufacturer_name="Samsung",
            manufacturer_country="KR",
            manufacturer_city="Seul",
            manufacturer_street="Hoinua",
            manufacturer_zip_code="31PTTK",
            year_of_construction=2025,
            family="Camera",
            sku="12345678027",
        )
        display = Product.objects.create(
            name="Display",
            description="Display used in various phones",
            supplier=self.samsung,
            manufacturer_name="Samsung",
            manufacturer_country="KR",
            manufacturer_city="Seul",
            manufacturer_street="Hoinua",
            manufacturer_zip_code="31PTTK",
            year_of_construction=2025,
            family="Display",
            sku="0987654334",
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
        self.iphone = Product.objects.create(
            name="iPhone 17",
            description="Latest iPhone model",
            supplier=self.apple,
            manufacturer_name="Apple",
            manufacturer_country="US",
            manufacturer_city="New York",
            manufacturer_street="Freedom Avenue",
            manufacturer_zip_code="7831TKP",
            year_of_construction=2025,
            family="Phone",
            sku="0987654334"
        )

        #add product material emissions
        processor_material_emission = MaterialEmission.objects.create(
            parent_product=self.processor,
            weight=0.5,
            reference=silicon_material,
        )
        processor_material_emission2 = MaterialEmission.objects.create(
            parent_product=self.processor,
            weight=0.5,
            reference=glass_material,
        )
        camera_material_emission = MaterialEmission.objects.create(
            parent_product=self.camera,
            weight=0.2,
            reference=glass_material,
        )
        display_material_emission = MaterialEmission.objects.create(
            parent_product=display,
            weight=0.3,
            reference=glass_material,
        )

        #add BoM items
        iphone_line_processor = ProductBoMLineItem.objects.create(
            parent_product=self.iphone,
            line_item_product=self.processor,
            quantity=1
        )
        iphone_line_camera = ProductBoMLineItem.objects.create(
            parent_product=self.iphone,
            line_item_product=self.camera,
            quantity=3
        )
        iphone_line_display = ProductBoMLineItem.objects.create(
            parent_product=self.iphone,
            line_item_product=display,
            quantity=1
        )

        #Add BoM item transport emissions
        iphone_line_processor_transport = TransportEmission.objects.create(
            parent_product=self.iphone,
            distance=2000,
            weight=0.5,
            reference=transport_air
        )
        EmissionBoMLink.objects.create(
            emission=iphone_line_processor_transport,
            line_item=iphone_line_processor,
        )

        iphone_line_camera_transport = TransportEmission.objects.create(
            parent_product=self.iphone,
            distance=500,
            weight=0.2,
            reference=transport_road,
        )
        EmissionBoMLink.objects.create(
            emission=iphone_line_camera_transport,
            line_item=iphone_line_camera,
        )

        iphone_line_display_transport = TransportEmission.objects.create(
            parent_product=self.iphone,
            distance=800,
            weight=0.3,
            reference=transport_road,
        )
        EmissionBoMLink.objects.create(
            emission=iphone_line_display_transport,
            line_item=iphone_line_display,
        )

        # Add production energy emissions to products
        self.iphone_assembly_emission = ProductionEnergyEmission.objects.create(
            parent_product=self.iphone,
            energy_consumption=2000,
            reference=assembly_line_reference,
        )

        # Add user energy emissions to products
        iphone_charging_emission = UserEnergyEmission.objects.create(
            parent_product=self.iphone,
            energy_consumption=500,
            reference=charging_phone
        )
        iphone_line_processor_update_emission = UserEnergyEmission.objects.create(
            parent_product=self.processor,
            energy_consumption=500,
            reference=update_processor,
        )

        # Add emission override factors
        EmissionOverrideFactor.objects.create(
            emission=iphone_line_processor_transport,
            lifecycle_stage=LifecycleStage.A3,
            co_2_emission_factor=69
        )

        # Add product emission override factors
        ProductEmissionOverrideFactor.objects.create(
            emission=display,
            lifecycle_stage=LifecycleStage.A1,
            co_2_emission_factor=300,
        )
        # Add product sharing requests
        ProductSharingRequest.objects.create(
            product=self.camera,
            requester=self.apple,
            status=ProductSharingRequestStatus.ACCEPTED
        )
        ProductSharingRequest.objects.create(
            product=display,
            requester=self.apple,
            status=ProductSharingRequestStatus.ACCEPTED
        )
        ProductSharingRequest.objects.create(
            product=self.processor,
            requester=self.apple,
            status=ProductSharingRequestStatus.REJECTED
        )

    def test_export_json(self):
        url = reverse("product-aas-json", args=[self.apple.id, self.iphone.id])
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
        url = reverse("product-aas-json", args=[self.samsung.id, self.camera.id])
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
        url = reverse("product-aas-json", args=[self.tsmc.id, self.processor.id])
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
        url = reverse("product-aas-json", args=[self.samsung.id, self.flashlight.id])
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
        url = reverse("product-aas-json", args=[self.apple.id, self.iphone.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_export_json_private_product(self):
        url = reverse("product-aas-json", args=[self.tsmc.id, self.quantum_pc.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_export_json_company_product_mismatch(self):
        url = reverse("product-aas-json", args=[self.apple.id, self.quantum_pc.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_export_xml(self):
        url = reverse("product-aas-xml", args=[self.apple.id, self.iphone.id])
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
        url = reverse("product-aas-xml", args=[self.samsung.id, self.camera.id])
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
        url = reverse("product-aas-xml", args=[self.tsmc.id, self.processor.id])
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
        url = reverse("product-aas-xml", args=[self.samsung.id, self.flashlight.id])
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
        url = reverse("product-aas-xml", args=[self.apple.id, self.iphone.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_export_xml_private_product(self):
        url = reverse("product-aas-xml", args=[self.tsmc.id, self.quantum_pc.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_export_xml_company_product_mismatch(self):
        url = reverse("product-aas-xml", args=[self.apple.id, self.quantum_pc.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_export_aasx(self):
        url = reverse("product-aas-aasx", args=[self.apple.id, self.iphone.id])
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
        url = reverse("product-aas-aasx", args=[self.samsung.id, self.camera.id])
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
        url = reverse("product-aas-aasx", args=[self.tsmc.id, self.processor.id])
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
        url = reverse("product-aas-aasx", args=[self.samsung.id, self.flashlight.id])
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
        url = reverse("product-aas-aasx", args=[self.apple.id, self.iphone.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_export_aasx_private_product(self):
        url = reverse("product-aas-aasx", args=[self.tsmc.id, self.quantum_pc.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_export_aasx_company_product_mismatch(self):
        url = reverse("product-aas-aasx", args=[self.apple.id, self.quantum_pc.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)