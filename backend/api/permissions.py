from rest_framework import permissions


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    '''Access for admin, author or read-only'''
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or (
                request.user.is_authenticated
                and (
                    obj.author == request.user
                    or request.user.is_superuser
                )
            )
        )
