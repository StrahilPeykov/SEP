from rest_framework import permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsCompanyMember(BasePermission):
    """
    Only allows access if request.user is a member of the Company instance.
    """
    def has_object_permission(self, request, view, obj):
        # obj is a Company
        return obj.user_is_member(request.user)


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