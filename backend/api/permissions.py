from rest_framework import permissions

from backend.users.models import UserRole


class IsAdmin(permissions.IsAuthenticated):
    '''Access for admin or superuser'''
    def has_permission(self, request, view):
        return super().has_permission(request, view) and (
            request.user.role == UserRole.ADMIN or request.user.is_superuser
        )


class IsAuthorOrReadOnly(permissions.BasePermission):
    '''Access for author or read-only'''
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
