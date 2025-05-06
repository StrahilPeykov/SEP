from rest_framework import permissions


class IsCompanyMemberOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        # Allow safe methods for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        # Allow unsafe methods only for company members
        return obj.user_has_permission(request.user)

class IsCompanyMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        # Allow only company members
        return obj.user_has_permission(request.user)