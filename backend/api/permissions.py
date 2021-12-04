from rest_framework import permissions

from backend.users.models import UserRole


class IsAdmin(permissions.IsAuthenticated):
    """Access for admin or superuser."""
    def has_permission(self, request, view):
        return super().has_permission(request, view) and (
            request.user.role == UserRole.ADMIN or request.user.is_superuser
        )
