from rest_framework.permissions import BasePermission

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        # return super().has_permission(request, view)
        return bool(request.user and request.user.is_authenticated and request.user.is_authenticated and request.user.is_admin)