# users/serializers.py
from django.contrib.auth import get_user_model, authenticate
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import EmailVerificationToken
from django.urls import reverse

User = get_user_model()

# ======== Admin Serializer =======================================================
class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id","username","email","first_name","last_name","is_active","is_staff","is_superuser","email_verified_at")

# ================================================================================

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    # Optional extras exposed at signup:
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name  = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "first_name", "last_name")

    def validate_email(self, v):
        return v.strip().lower()

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Create email verification token (24h expiry)
        token = EmailVerificationToken.objects.create(
            user=user,
            expires_at=timezone.now() + timezone.timedelta(hours=24),
        )

        # Build verification URL (frontend or API endpoint)
        request = self.context.get("request")
        verify_path = reverse("users:verify-email")  # defined in users/urls.py
        verify_url = f"{request.build_absolute_uri(verify_path)}?token={token.token}"

        # Send email (MVP: print to console; plug in real email later)
        self._send_verification_email(user.email, verify_url)
        return user

    @staticmethod
    def _send_verification_email(email, url):
        # TODO: replace with real email sender (SendGrid/SES/etc.)
        print(f"[DEV] Send email verification to {email}: {url}")


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.UUIDField()

    def validate(self, attrs):
        token_value = attrs["token"]
        try:
            token_obj = EmailVerificationToken.objects.select_related("user").get(token=token_value)
        except EmailVerificationToken.DoesNotExist:
            raise serializers.ValidationError("Invalid token.")

        if token_obj.consumed_at is not None:
            raise serializers.ValidationError("Token already used.")
        if timezone.now() >= token_obj.expires_at:
            raise serializers.ValidationError("Token has expired.")

        attrs["token_obj"] = token_obj
        return attrs

    def save(self, **kwargs):
        token_obj: EmailVerificationToken = self.validated_data["token_obj"]
        user = token_obj.user
        user.mark_email_verified()
        token_obj.mark_consumed()
        return user


class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, v):
        return v.strip().lower()

    def validate(self, attrs):
        email = attrs["email"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("If the email exists, a message will be sent.")  # don’t leak users

        if user.is_verified:
            raise serializers.ValidationError("Email is already verified.")

        attrs["user"] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        token = EmailVerificationToken.objects.create(
            user=user,
            expires_at=timezone.now() + timezone.timedelta(hours=24),
        )
        request = self.context.get("request")
        from django.urls import reverse
        verify_path = reverse("users:verify-email")
        verify_url = f"{request.build_absolute_uri(verify_path)}?token={token.token}"
        SignupSerializer._send_verification_email(user.email, verify_url)
        return {"detail": "If the email exists, a verification link has been sent."}


class LoginTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    SimpleJWT login with an extra check: require verified email before issuing tokens.
    """
    def validate(self, attrs):
        # Allow login by username or email (lowercased)
        identifier = attrs.get("username")  # SimpleJWT uses 'username' key
        password = attrs.get("password")

        user = None
        if identifier:
            identifier_l = identifier.strip().lower()
            # Try email first
            try:
                user = User.objects.get(email=identifier_l)
            except User.DoesNotExist:
                # Fallback to username
                user = authenticate(request=self.context.get("request"),
                                    username=identifier, password=password)
                if user is None:
                    # Try username lookup if auth backend needs explicit check
                    try:
                        user_obj = User.objects.get(username=identifier)
                        if not user_obj.check_password(password):
                            user_obj = None
                        user = user_obj
                    except User.DoesNotExist:
                        user = None

        if user is None:
            # If email path: authenticate explicitly
            try:
                user_obj = User.objects.get(email=identifier_l)
                if not user_obj.check_password(password):
                    user_obj = None
                user = user_obj
            except Exception:
                pass

        if user is None:
            raise serializers.ValidationError("Invalid credentials.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        if not user.is_verified:
            raise serializers.ValidationError("Email not verified.")

        # Let SimpleJWT create tokens
        data = super().validate({"username": user.username, "password": password})
        # Optionally add user info
        data.update({
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        })
        return data
