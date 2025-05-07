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
from core.views.product_view_set import ProductViewSet

router = DefaultRouter()
router.register(r"companies", CompanyViewSet)

company_router = NestedDefaultRouter(router, r"companies", lookup="company")
company_router.register(r"products", ProductViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path("api/", include(company_router.urls)),
    path("api/register/", RegisterView.as_view({"post": "create"}), name="register"),
    path("api/user_profile/", UserProfileView.as_view(), name="user_profile"),
    path("api/change_password/", ChangePasswordView.as_view(), name="change_password"),
    path("api/login/", LoginView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", RefreshView.as_view(), name="token_refresh"),
    path("api/populate_db/", populate_db, name="populate_db"),
    path("api/destroy_db/", destroy_db, name="destroy_db"),
]