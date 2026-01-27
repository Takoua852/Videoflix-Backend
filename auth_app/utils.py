from rest_framework_simplejwt.tokens import RefreshToken


def create_jwt_tokens(user):
    """Create JWT access and refresh tokens for a given user."""
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }