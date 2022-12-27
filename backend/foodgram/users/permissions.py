from rest_framework import permissions


class IsGuest(permissions.BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_authenticated
