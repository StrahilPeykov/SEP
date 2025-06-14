"""
This file contains the generic setup functions of test cases that that are called in tests setups and extended if needed
"""

from django.urls import reverse
from rest_framework import status
from core.models import User, EmissionBoMLink, ProductBoMLineItem, Product, CompanyMembership, Company
from core.models import UserEnergyEmission, ProductionEnergyEmission, TransportEmission
from core.models import  UserEnergyEmissionReference, ProductionEnergyEmissionReference, TransportEmissionReference
from core.models import UserEnergyEmissionReferenceFactor, TransportEmissionReferenceFactor, \
    ProductionEnergyEmissionReferenceFactor , LifecycleStage
from core.models import ProductSharingRequestStatus, ProductSharingRequest
from core.models.product import ProductEmissionOverrideFactor
from core.models import EmissionOverrideFactor


def paint_companies_setup(self):
    """
    Generic setup function that consists of Paint companies. Simpler setup
    """

    # Create two users
    self.red_company_user1 = User.objects.create_user(username="1@redcompany.com", email="1@redcompany.com",
                                                      password="1234567890")
    self.red_company_user2 = User.objects.create_user(username="2@redcompany.com", email="2@redcompany.com",
                                                      password="1234567890")
    self.blue_company_user1 = User.objects.create_user(username="1@bluecompany.com", email="1@bluecompany.com",
                                                       password="1234567890")
    self.blue_company_user2 = User.objects.create_user(username="2@bluecompany.com", email="2@bluecompany.com",
                                                       password="1234567890")
    self.green_company_user1 = User.objects.create_user(username="1@greencompany.com", email="1@greencompany.com",
                                                        password="1234567890")
    self.green_company_user2 = User.objects.create_user(username="2@greencompany.com", email="2@greencompany.com",
                                                        password="1234567890")

    # Obtain JWT for user1
    url = reverse("token_obtain_pair")
    resp = self.client.post(
        url, {"username": "1@redcompany.com", "password": "1234567890"}, format="json"
    )
    self.assertEqual(resp.status_code, status.HTTP_200_OK)
    self.access_token = resp.data["access"]
    self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    #Create reference company
    self.references = Company.objects.create(
        name = "Reference",
        vat_number = "N/A",
        business_registration_number="REFERENCE",
        is_reference=True,
        auto_approve_product_sharing_requests=True
    )

    # Create an existing company
    self.red_company = Company.objects.create(
        name="Red company BV",
        vat_number="VATRED",
        business_registration_number="NL123456"
    )
    self.green_company = Company.objects.create(
        name="Green company BV",
        vat_number="VATGREEN",
        business_registration_number="NL654321"
    )
    self.blue_company = Company.objects.create(
        name="Blue company BV",
        vat_number="VATBLUE",
        business_registration_number="NL938321"
    )

    # Add users to companies
    CompanyMembership.objects.create(user=self.red_company_user1, company=self.red_company)
    CompanyMembership.objects.create(user=self.red_company_user2, company=self.red_company)
    CompanyMembership.objects.create(user=self.blue_company_user1, company=self.blue_company)
    CompanyMembership.objects.create(user=self.blue_company_user2, company=self.blue_company)
    CompanyMembership.objects.create(user=self.green_company_user1, company=self.green_company)
    CompanyMembership.objects.create(user=self.green_company_user2, company=self.green_company)

    # Add Products
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
        family="Plan",
        sku="111222333444",
        is_public=False
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
        family="Plan",
        sku="111222333444",
        is_public=False
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
    self.green_paint = Product.objects.create(
        name="Green Paint",
        description="Green Paint",
        supplier=self.green_company,
        manufacturer_name="Green Company",
        manufacturer_country="NL",
        manufacturer_city="Utrecht",
        manufacturer_street="Street 3",
        manufacturer_zip_code="9012EF",
        year_of_construction=2025,
        family="General",
        sku="GRNPROD001",
        is_public=True
    )
    self.green_secret_plans = Product.objects.create(
        name="Secret Plan Green",
        description="Secret Plan Green",
        supplier=self.green_company,
        manufacturer_name="Green company",
        manufacturer_country="NL",
        manufacturer_city="Eindhoven",
        manufacturer_street="De Zaale",
        manufacturer_zip_code="5612AZ",
        year_of_construction=2025,
        family="Plan",
        sku="111222333444",
        is_public=False
    )

def tech_companies_setup(self):
    """
    Generic setup function that consists of Tech companies. More complex setup
    """

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

    # Create reference company
    self.references = Company.objects.create(
        name="Reference",
        vat_number="N/A",
        business_registration_number="REFERENCE",
        is_reference=True,
        auto_approve_product_sharing_requests=True
    )

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

    #Reference products
    self.glass_material = Product.objects.create(
        name="Glass Reference",
        description="Glass Reference",
        supplier=self.references,
        manufacturer_name="Reference",
        manufacturer_country="AQ",
        manufacturer_city="Anor Lando",
        manufacturer_street="Nightmare of Mensis",
        manufacturer_zip_code="#fc0a8b",
        year_of_construction=2025,
        family="Reference",
        sku="N/A",
    )
    ProductEmissionOverrideFactor.objects.create(
        product=self.glass_material,
        lifecycle_stage=LifecycleStage.A1,
        co_2_emission_factor_biogenic=0.5,
    )

    self.silicon_material = Product.objects.create(
        name="Silicon Reference",
        description="Silicon Reference",
        supplier=self.references,
        manufacturer_name="Reference",
        manufacturer_country="EC",
        manufacturer_city="Yharnam",
        manufacturer_street="Curch of Yorshka",
        manufacturer_zip_code="#09e80d",
        year_of_construction=2025,
        family="Reference",
        sku="N/A",
    )
    ProductEmissionOverrideFactor.objects.create(
        product=self.silicon_material,
        lifecycle_stage=LifecycleStage.A2,
        co_2_emission_factor_biogenic=0.3,
    )
    ProductEmissionOverrideFactor.objects.create(
        product=self.silicon_material,
        lifecycle_stage=LifecycleStage.A1,
        co_2_emission_factor_biogenic=0.2,
    )

    # Add transport emission references
    self.transport_air = TransportEmissionReference.objects.create(common_name="Air transport")
    TransportEmissionReferenceFactor.objects.create(
        emission_reference=self.transport_air,
        lifecycle_stage=LifecycleStage.A3,
        co_2_emission_factor_biogenic=0.2,
    )
    TransportEmissionReferenceFactor.objects.create(
        emission_reference=self.transport_air,
        lifecycle_stage=LifecycleStage.A4,
        co_2_emission_factor_biogenic=0.3,
    )

    self.transport_road = TransportEmissionReference.objects.create(common_name="Road transport")
    TransportEmissionReferenceFactor.objects.create(
        emission_reference=self.transport_road,
        lifecycle_stage=LifecycleStage.A3,
        co_2_emission_factor_biogenic=0.05,
    )

    # Add production energy emission references
    self.assembly_line_reference = ProductionEnergyEmissionReference.objects.create(common_name="Assembly line")
    ProductionEnergyEmissionReferenceFactor.objects.create(
        emission_reference=self.assembly_line_reference,
        lifecycle_stage=LifecycleStage.A3,
        co_2_emission_factor_biogenic=0.4,
    )

    # Add user energy emission references
    self.charging_phone = UserEnergyEmissionReference.objects.create(common_name="Charging phone")
    UserEnergyEmissionReferenceFactor.objects.create(
        emission_reference=self.charging_phone,
        lifecycle_stage=LifecycleStage.A5,
        co_2_emission_factor_biogenic=0.2,
    )
    self.update_processor = UserEnergyEmissionReference.objects.create(common_name="Update processor")
    UserEnergyEmissionReferenceFactor.objects.create(
        emission_reference=self.update_processor,
        lifecycle_stage=LifecycleStage.A5,
        co_2_emission_factor_biogenic=0.2,
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
    self.display = Product.objects.create(
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

    # Add material references
    self.processor_material_reference = ProductBoMLineItem.objects.create(
        parent_product=self.processor,
        quantity=0.5,
        line_item_product=self.silicon_material,
    )
    self.processor_material_reference2 = ProductBoMLineItem.objects.create(
        parent_product=self.processor,
        quantity=0.5,
        line_item_product=self.glass_material,
    )
    self.camera_material_reference = ProductBoMLineItem.objects.create(
        parent_product=self.camera,
        quantity=0.2,
        line_item_product=self.glass_material,
    )
    self.display_material_reference = ProductBoMLineItem.objects.create(
        parent_product=self.display,
        quantity=0.3,
        line_item_product=self.glass_material,
    )

    # Add BoM items
    self.iphone_line_processor = ProductBoMLineItem.objects.create(
        parent_product=self.iphone,
        line_item_product=self.processor,
        quantity=1
    )
    self.iphone_line_camera = ProductBoMLineItem.objects.create(
        parent_product=self.iphone,
        line_item_product=self.camera,
        quantity=3
    )
    self.iphone_line_display = ProductBoMLineItem.objects.create(
        parent_product=self.iphone,
        line_item_product=self.display,
        quantity=1
    )

    # Add BoM item transport emissions
    self.iphone_line_processor_transport = TransportEmission.objects.create(
        parent_product=self.iphone,
        distance=2000,
        weight=0.5,
        reference=self.transport_air
    )
    EmissionBoMLink.objects.create(
        emission=self.iphone_line_processor_transport,
        line_item=self.iphone_line_processor,
    )

    self.iphone_line_camera_transport = TransportEmission.objects.create(
        parent_product=self.iphone,
        distance=500,
        weight=0.2,
        reference=self.transport_road,
    )
    EmissionBoMLink.objects.create(
        emission=self.iphone_line_camera_transport,
        line_item=self.iphone_line_camera,
    )

    self.iphone_line_display_transport = TransportEmission.objects.create(
        parent_product=self.iphone,
        distance=800,
        weight=0.3,
        reference=self.transport_road,
    )
    EmissionBoMLink.objects.create(
        emission=self.iphone_line_display_transport,
        line_item=self.iphone_line_display,
    )

    # Add production energy emissions to products
    self.iphone_assembly_emission = ProductionEnergyEmission.objects.create(
        parent_product=self.iphone,
        energy_consumption=2000,
        reference=self.assembly_line_reference,
    )

    # Add user energy emissions to products
    self.iphone_charging_emission = UserEnergyEmission.objects.create(
        parent_product=self.iphone,
        energy_consumption=500,
        reference=self.charging_phone
    )
    self.iphone_line_processor_update_emission = UserEnergyEmission.objects.create(
        parent_product=self.processor,
        energy_consumption=500,
        reference=self.update_processor,
    )

    # Add emission override factors
    self.iphone_iphone_line_processor_transport_override = EmissionOverrideFactor.objects.create(
        emission=self.iphone_line_processor_transport,
        lifecycle_stage=LifecycleStage.A3,
        co_2_emission_factor_biogenic=69
    )

    # Add product emission override factors
    ProductEmissionOverrideFactor.objects.create(
        product=self.display,
        lifecycle_stage=LifecycleStage.A1,
        co_2_emission_factor_biogenic=300,
    )

    # Add product sharing requests
    ProductSharingRequest.objects.create(
        product=self.camera,
        requester=self.apple,
        status=ProductSharingRequestStatus.ACCEPTED
    )
    ProductSharingRequest.objects.create(
        product=self.display,
        requester=self.apple,
        status=ProductSharingRequestStatus.ACCEPTED
    )
    ProductSharingRequest.objects.create(
        product=self.processor,
        requester=self.apple,
        status=ProductSharingRequestStatus.REJECTED
    )