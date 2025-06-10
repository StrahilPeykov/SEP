import sys

from django.contrib.auth.admin import UserAdmin

from core.models import *
from .ai_conversation_log_admin import AIConversationLogAdmin
from .company_admin import CompanyAdmin
from .product_admin import ProductAdmin
from .emission_admin import *
from .production_energy_reference_emission_admin import *
from .transport_reference_emission_admin import *
from .user_energy_emission_admin import *

admin.site.register(User, UserAdmin)

if 'runserver' in sys.argv:
    admin.site.site_header = "CarbonInsight Admin [Local build]"
    admin.site.site_title = "CarbonInsight Admin [Local build]"
else:
    admin.site.site_header = "CarbonInsight Admin [Production]"
    admin.site.site_title = "CarbonInsight Admin [Production]"
admin.site.index_title = "Welcome to the CarbonInsight admin portal"