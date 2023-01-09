from rest_framework import permissions


class IsGuest(permissions.BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsAdminOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_staff
                or obj.author == request.user)
