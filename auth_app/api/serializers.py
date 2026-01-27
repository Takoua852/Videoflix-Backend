from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

User = get_user_model()

# ------------------- Register -------------------


class RegisterSerializer(serializers.ModelSerializer):
    """Handles user registration with password confirmation and validation."""

    confirmed_password = serializers.CharField(write_only=True)
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="A user with that email already exists."
            )
        ]
    )

    class Meta:
        model = User
        fields = ("id", "email", "password", "confirmed_password")
        extra_kwargs = {"email": {"required": True}}

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("confirmed_password"):
            raise serializers.ValidationError(
                {"confirmed_password": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirmed_password')
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False  # User is inactive until email activation
        )
        return user

# ------------------- Password Reset Request -------------------


class PasswordResetSerializer(serializers.Serializer):
    """Validates email for password reset request."""

    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "User with this email does not exist.")
        return value

# ------------------- Password Reset Confirm -------------------


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Validates and sets a new password during password reset."""

    new_password = serializers.CharField(
        write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })
        validate_password(attrs["new_password"])
        return attrs
