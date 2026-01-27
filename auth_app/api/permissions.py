from rest_framework.permissions import BasePermission

class HasRefreshTokenCookie(BasePermission):
    """
    Allows access only if refresh_token cookie exists.
    """
    def has_permission(self, request, view):
        return 'refresh_token' in request.COOKIES
