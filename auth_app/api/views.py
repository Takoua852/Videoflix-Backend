from rest_framework import generics, status
from .serializers import RegisterSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model, authenticate
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from auth_app.tokens import account_activation_token, password_reset_token
from .permissions import HasRefreshTokenCookie
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.db import transaction
from django_rq import get_queue
from auth_app.tasks import send_activation_email_task, send_password_reset_email_task

User = get_user_model()

# ------------------- Registration & Activation -------------------


class RegisterView(generics.CreateAPIView):
    """
    POST /api/register/
    Registers a new user and sends activation email.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"detail": "Registration failed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = serializer.save()

        # UID & Token
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)

        activation_link = (
            f"{settings.FRONTEND_URL}/pages/auth/activate.html"
            f"?uid={uidb64}&token={token}"
        )

        def enqueue_email():
            queue = get_queue("default", autocommit=True)
            queue.enqueue(send_activation_email_task, user.email, activation_link)

        transaction.on_commit(enqueue_email)

        return Response(
            {"detail": "Registration successful. Please check your email to activate your account."},
            status=status.HTTP_201_CREATED
        )


class ActivateAccountView(APIView):
    """GET /api/activate/<uidb64>/<token>/ - Activates a user account."""
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response(
                {"message": "Invalid activation link."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.is_active:
            return Response(
                {"message": "Account already activated."},
                status=status.HTTP_200_OK
            )

        if account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()

            return Response(
                {"message": "Account successfully activated."},
                status=status.HTTP_200_OK
            )

        return Response(
            {"message": "Activation failed."},
            status=status.HTTP_400_BAD_REQUEST
        )
# ------------------- Login -------------------


class LoginView(APIView):

    """POST /api/login/ - Authenticates user and sets HTTP-only cookies."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"detail": "Email and password are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=email, password=password)

        if user is None:
            return Response({"detail": "Invalid credentials."},
                            status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({"detail": "Account not activated."},
                            status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        response = Response({
            "detail": "Login successful",
            "user": {"id": user.id, "email": user.email}
        }, status=status.HTTP_200_OK)

        response.set_cookie(
            key="access_token",
            value=str(access),
            httponly=True,
            secure=False,  # lokal False, in prod True
            samesite="Lax",
        )
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=False,
            samesite="Lax",
        )

        return response

# ------------------- Logout -------------------


class LogoutView(APIView):
    """POST /api/logout/ - Logs out user, deletes cookies, blacklists refresh token."""

    permission_classes = [HasRefreshTokenCookie]
    authentication_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response({"detail": "No refresh token provided."},
                            status=status.HTTP_400_BAD_REQUEST)

        token = RefreshToken(refresh_token)
        token.blacklist()

        response = Response(
            {"detail": "Logout successful! All tokens deleted."},
            status=status.HTTP_200_OK)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response

# ------------------- Token Refresh -------------------


class TokenRefreshView(APIView):
    """POST /api/token/refresh/ - Refreshes access token using cookie refresh token."""
    permission_classes = [HasRefreshTokenCookie]
    authentication_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "No refresh token provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)
        except TokenError:
            return Response(
                {"detail": "Token refresh failed."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # neuen access_token als HttpOnly Cookie setzen
        response = Response(
            {"detail": "Token refreshed", "access": access_token},
            status=status.HTTP_200_OK
        )
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # lokal False, in prod True
            samesite="Lax"
        )

        return response

# ------------------- Password Reset -------------------


class PasswordResetView(APIView):
    """POST /api/password_reset/ - Sends password reset link to user's email."""
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = User.objects.get(email=email)

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = password_reset_token.make_token(user)

        reset_link = (f"{settings.FRONTEND_URL}/pages/auth/confirm_password.html"
                      f"?uid={uidb64}&token={token}")

        def enqueue_email():
            queue = get_queue("default", autocommit=True)
            queue.enqueue(send_password_reset_email_task, user.email, reset_link)

        transaction.on_commit(enqueue_email)

        return Response({"detail": "An email has been sent to reset your password."},
                        status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """POST /api/password_confirm/<uidb64>/<token>/ - Resets user's password."""
    permission_classes = []
    authentication_classes = []

    def post(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "Invalid link."}, status=400)

        if not password_reset_token.check_token(user, token):
            return Response({"detail": "Invalid or expired token."}, status=400)

        new_password = serializer.validated_data["new_password"]
        user.set_password(new_password)
        user.save()

        return Response({"detail": "Password successfully reset."}, status=200)
