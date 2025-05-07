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


class IsUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow users to edit their own profile.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the user themselves
        return obj == request.user
