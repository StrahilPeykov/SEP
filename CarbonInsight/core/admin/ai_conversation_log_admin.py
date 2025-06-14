from django.contrib import admin

from core.models import Company, CompanyMembership, Product, AIConversationLog


@admin.register(AIConversationLog)
class AIConversationLogAdmin(admin.ModelAdmin):
    """
    Defines the fields to be presented and how they are shown in the admin panel for AIConversationLog.
    """

    model = Company
    list_display = ("user", "product", "created_at",)
    search_fields = ("user__username", "product__name", "user_prompt", "response",)
    ordering = ("-created_at",)
    readonly_fields = ("user", "product", "user_prompt", "instructions", "response", "created_at",)