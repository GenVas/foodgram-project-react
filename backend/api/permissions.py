from rest_framework import permissions

from users.models import UserRole


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


class IsAdminOrReadOnly(IsAdmin):
    """Manage permissions.
    SAFE methods allowed for anyone,
    inlcuding not authenticateed.
    `POST` allowed for admin.
    Other methods allowed for admin.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or super().has_permission(request, view))
