"""
URL configuration for CarbonInsight project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from core.views import *
from core.views.product_bom_line_item_view_set import ProductBoMLineItemViewSet
from core.views.company_view_set import MyCompaniesViewSet
from core.views.company_view_set import CompanyUserViewSet
from core.views.product_view_set import ProductViewSet
from core.views.production_energy_view_set import ProductionEnergyEmissionViewSet
from core.views.transport_emission_view_set import TransportEmissionViewSet
from core.views.user_energy_view_set import UserEnergyEmissionViewSet

router = DefaultRouter()
router.register(r"companies/my", MyCompaniesViewSet, basename="companies-my")
router.register(r"companies", CompanyViewSet)
router.register(r"reference/transport", TransportEmissionReferenceViewSet, basename="transport-reference")
router.register(r"reference/user_energy", UserEnergyEmissionReferenceViewSet, basename="user-energy-reference")
router.register(r"reference/production_energy", ProductionEnergyEmissionReferenceViewSet, basename="production-energy-reference")

company_router = NestedDefaultRouter(router, r"companies", lookup="company")
company_router.register(r"products", ProductViewSet)
company_router.register(r"users", CompanyUserViewSet, basename="company-users")
company_router.register(
    r"product_sharing_requests",
    ProductSharingRequestViewSet,
    basename="product_sharing_requests"
)

product_router = NestedDefaultRouter(company_router, r"products", lookup="product")
product_router.register(r"bom", ProductBoMLineItemViewSet, basename="product-bom")
product_router.register(r"emissions/transport", TransportEmissionViewSet, basename="product-transport-emissions")
product_router.register(r"emissions/user_energy", UserEnergyEmissionViewSet, basename="product-user-energy-emissions")
product_router.register(r"emissions/production_energy", ProductionEnergyEmissionViewSet, basename="product-production-energy-emissions")

urlpatterns = [
    path("api/", include(router.urls)),
    path("api/", include(company_router.urls)),
    path("api/", include(product_router.urls)),
    path("api/register/", RegisterView.as_view({"post": "create"}), name="register"),
    path("api/user_profile/", UserProfileView.as_view(), name="user_profile"),
    path("api/change_password/", ChangePasswordView.as_view(), name="change_password"),
    path("api/login/", LoginView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", RefreshView.as_view(), name="token_refresh")
]