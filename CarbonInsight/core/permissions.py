from rest_framework import permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS

from core.models import Company


class IsCompanyMember(BasePermission):
    """
    Allows access only if request.user is authenticated
    and a member of the company identified by company_pk.
    """
    def has_permission(self, request, view):
        # must be logged in
        if not request.user or not request.user.is_authenticated:
            return False

        # only nested company routes include company_pk
        company_pk = view.kwargs.get('company_pk')
        if not company_pk:
            return False

        try:
            company = Company.objects.get(pk=company_pk)
        except Company.DoesNotExist:
            return False

        return company.user_is_member(request.user)

    def has_object_permission(self, request, view, obj):
        # obj is a Company for generic views or a Model instance for nested ones
        # if obj is CompanyMembership through obj.company:
        company = getattr(obj, 'company', obj)
        return company.user_is_member(request.user)


class CanEditCompany(BasePermission):
    """
    Allows POST on /companies/ to any authenticated user,
    but PUT/PATCH/DELETE only if member of that company.
    """
    def has_permission(self, request, view):
        # list and create are global actions:
        if view.action in ('list', 'retrieve', 'create'):
            return request.user and request.user.is_authenticated
        # for other actions, will check object permission
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # only allow unsafe methods if member
        if request.method in SAFE_METHODS:
            return True
        return obj.user_is_member(request.user)


class ProductPermission(BasePermission):
    """
    Handles:
      - POST  -> only if you can edit parent company
      - GET   -> if is_public or you can edit parent company
      - PUT/PATCH/DELETE -> only if you can edit parent company
    """
    def _is_company_member(self, request, view):
        company = view.get_parent_company()
        return company.user_is_member(request.user)

    def has_permission(self, request, view):
        # Must be authenticated for everything
        if not (request.user and request.user.is_authenticated):
            return False

        # POST: only if can edit parent
        if view.action == 'create':
            return self._is_company_member(request, view)

        # GET list & retrieve: defer to object / get_queryset
        return True

    def has_object_permission(self, request, view, obj):
        # SAFE (GET detail) -> allow if public or member
        if request.method in SAFE_METHODS:
            return obj.is_public or self._is_company_member(request, view)
        # unsafe -> only members
        return self._is_company_member(request, view)


class ProductSubAPIPermission(BasePermission):
    """
    Grants access only if request.user is authenticated
    and is a member of the parent company.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return view.get_parent_company().user_is_member(request.user)

    def has_object_permission(self, request, view, obj):
        return view.get_parent_company().user_is_member(request.user)