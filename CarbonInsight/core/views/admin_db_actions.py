from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import RedirectView
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework import status
from core.models import Company, CompanyMembership, MaterialEmission, MaterialEmissionReference, Product, \
    ProductBoMLineItem, TransportEmission, TransportEmissionReference, Emission, MaterialEmissionReferenceFactor, \
    TransportEmissionReferenceFactor
from core.models.lifecycle_stage import LifecycleStage

User = get_user_model()

@extend_schema(
    tags=["TESTING"],
    summary="Populate the database with test data",
    description="FOR TESTING PURPOSES ONLY. "
                "Creates four test users, four test companies, and products for them. "
                "Login with admin@example.com and 1234567890. "
                "Password for all other users is the same."
)
@api_view(['POST'])
@permission_classes([AllowAny])
def populate_db(request):
    # Create test users
    admin_user = User.objects.create_user(username="admin@example.com", email="admin@example.com", password="1234567890")
    admin_user.is_superuser = True
    admin_user.is_staff = True
    admin_user.save()
    apple_user_1 = User.objects.create_user(username="apple1@apple.com", email="apple1@apple.com", password="1234567890")
    apple_user_2 = User.objects.create_user(username="apple2@apple.com", email="apple2@apple.com", password="1234567890")
    samsung_user_1 = User.objects.create_user(username="samsung1@samsung.com", email="samsung1@samsung.com", password="1234567890")
    samsung_user_2 = User.objects.create_user(username="samsung2@samsung.com", email="samsung2@samsung.com", password="1234567890")
    corning_user_1 = User.objects.create_user(username="corning1@corning.com", email="corning1@corning.com", password="1234567890")
    corning_user_2 = User.objects.create_user(username="corning2@corning.com", email="corning2@corning.com", password="1234567890")
    tsmc_user_1 = User.objects.create_user(username="tsmc1@tsmc.com", email="tsmc1@tsmc.com", password="1234567890")
    tsmc_user_2 = User.objects.create_user(username="tsmc2@tsmc.com", email="tsmc2@tsmc.com", password="1234567890")


    # Create test companies
    apple = Company.objects.create(
        name="Apple Inc.",
        vat_number="TEST123456",
        business_registration_number="REG123456"
    )
    samsung = Company.objects.create(
        name="Samsung Electronics",
        vat_number="TEST654321",
        business_registration_number="REG654321"
    )
    corning = Company.objects.create(
        name="Corning Inc.",
        vat_number="TEST789012",
        business_registration_number="REG789012"
    )
    tsmc = Company.objects.create(
        name="Taiwan Semiconductor Manufacturing Company",
        vat_number="TEST345678",
        business_registration_number="REG345678"
    )

    # Create company memberships
    CompanyMembership.objects.create(user=admin_user, company=apple)
    CompanyMembership.objects.create(user=admin_user, company=samsung)
    CompanyMembership.objects.create(user=admin_user, company=corning)
    CompanyMembership.objects.create(user=admin_user, company=tsmc)
    CompanyMembership.objects.create(user=apple_user_1, company=apple)
    CompanyMembership.objects.create(user=apple_user_2, company=apple)
    CompanyMembership.objects.create(user=samsung_user_1, company=samsung)
    CompanyMembership.objects.create(user=samsung_user_2, company=samsung)
    CompanyMembership.objects.create(user=corning_user_1, company=corning)
    CompanyMembership.objects.create(user=corning_user_2, company=corning)
    CompanyMembership.objects.create(user=tsmc_user_1, company=tsmc)
    CompanyMembership.objects.create(user=tsmc_user_2, company=tsmc)

    # Add raw materials
    glass_material = MaterialEmissionReference.objects.create(name="Glass")
    MaterialEmissionReferenceFactor.objects.create(
        emission_reference=glass_material,
        lifecycle_stage = LifecycleStage.A1,
        co_2_emission_factor=0.5,
    )
    silicon_material = MaterialEmissionReference.objects.create(name="Silicon")
    MaterialEmissionReferenceFactor.objects.create(
        emission_reference=silicon_material,
        lifecycle_stage = LifecycleStage.A2,
        co_2_emission_factor=0.3,
    )

    # Add products to companies
    processor = Product.objects.create(
        name="A14 processor",
        description="Main processor used in iPhones",
        supplier=tsmc,
    )
    processor_material_emission  = MaterialEmission.objects.create(
        content_type=ContentType.objects.get_for_model(processor),
        content_object=processor,
        weight=0.5,
        reference=silicon_material,
    )
    camera = Product.objects.create(
        name="Camera module",
        description="Camera module used in various phones",
        supplier=samsung,
    )
    camera_material_emission = MaterialEmission.objects.create(
        content_type=ContentType.objects.get_for_model(camera),
        content_object=camera,
        weight=0.2,
        reference=glass_material,
    )
    display = Product.objects.create(
        name="Display",
        description="Display used in various phones",
        supplier=samsung,
    )
    display_self_estimated_pollution = MaterialEmission.objects.create(
        content_type=ContentType.objects.get_for_model(display),
        content_object=display,
        weight=0.3,
        reference=glass_material,
    )
    iphone = Product.objects.create(
        name="iPhone 17",
        description="Latest iPhone model",
        supplier=apple
    )
    iphone_line_processor = ProductBoMLineItem.objects.create(
        parent_product=iphone,
        line_item_product=processor,
        quantity=1
    )

    transport_air = TransportEmissionReference.objects.create(name="Air transport")
    TransportEmissionReferenceFactor.objects.create(
        emission_reference=transport_air,
        lifecycle_stage=LifecycleStage.A3,
        co_2_emission_factor=0.2,
    )
    transport_road = TransportEmissionReference.objects.create(name="Road transport")
    TransportEmissionReferenceFactor.objects.create(
        emission_reference=transport_road,
        lifecycle_stage=LifecycleStage.A3,
        co_2_emission_factor=0.05,
    )
    iphone_line_processor_transport = TransportEmission.objects.create(
        content_type=ContentType.objects.get_for_model(iphone_line_processor),
        content_object=iphone_line_processor,
        distance=2000,
        weight=0.5,
        reference=transport_air,
    )
    iphone_line_camera = ProductBoMLineItem.objects.create(
        parent_product=iphone,
        line_item_product=camera,
        quantity=3
    )
    iphone_line_camera_transport = TransportEmission.objects.create(
        content_type=ContentType.objects.get_for_model(iphone_line_camera),
        content_object=iphone_line_camera,
        distance=500,
        weight=0.2,
        reference=transport_road,
    )
    iphone_line_display = ProductBoMLineItem.objects.create(
        parent_product=iphone,
        line_item_product=display,
        quantity=1
    )
    iphone_line_display_transport = TransportEmission.objects.create(
        content_type=ContentType.objects.get_for_model(iphone_line_display),
        content_object=iphone_line_display,
        distance=800,
        weight=0.3,
        reference=transport_road,
    )

    # Log in as the admin user
    login(request, admin_user)

    # Redirect to the admin page
    return redirect(reverse("admin:index"))

@extend_schema(
    tags=["TESTING"],
    summary="Delete entire database",
    description="FOR TESTING PURPOSES ONLY. "
                "Deletes all data from the database. "
                "Use with caution."
)
@api_view(['POST'])
@permission_classes([AllowAny])
def destroy_db(request):
    # Delete all data
    ProductBoMLineItem.objects.all().delete()
    Product.objects.all().delete()
    Emission.objects.all().delete()
    MaterialEmissionReference.objects.all().delete()
    MaterialEmissionReferenceFactor.objects.all().delete()
    TransportEmissionReference.objects.all().delete()
    TransportEmissionReferenceFactor.objects.all().delete()
    CompanyMembership.objects.all().delete()
    Company.objects.all().delete()
    User.objects.all().delete()

    return Response({"status": "Database destroyed"}, status=status.HTTP_200_OK)
