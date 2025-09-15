import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.utils import timezone


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    - Keeps username-based login (safe default).
    - Enforces case-insensitive unique email.
    - Tracks email verification timestamp.
    - Adds optional profile fields & audits.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Keep username from AbstractUser; add robust email handling
    email = models.EmailField(unique=True) 
    email_verified_at = models.DateTimeField(null=True, blank=True)

    # Optional profile/audit fields
    avatar_url = models.URLField(null=True, blank=True)
    timezone = models.CharField(max_length=64, default="UTC")
    last_password_change_at = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return self.username or self.email

    def mark_email_verified(self):
        if not self.email_verified_at:
            self.email_verified_at = timezone.now()
            self.save(update_fields=["email_verified_at"])

    @property
    def is_verified(self) -> bool:
        return self.email_verified_at is not None

    def save(self, *args, **kwargs):
        #   Normalize email to lowercase before saving
        if self.email:
            self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

    class Meta:
        # Case-insensitive uniqueness for email at the DB level
        constraints = [
            UniqueConstraint(
                Lower("email"),
                name="users_user_email_ci_unique",
                violation_error_message="A user with this email already exists.",
            )
        ]
        indexes = [
            models.Index(Lower("email"), name="users_email_ci_idx"),
        ]


class EmailVerificationToken(models.Model):
    """
    Tokens for verifying user email addresses.
    - UUID token (safe to expose in links)
    - Expiry + consumed tracking
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="verification_tokens"
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)

    # Optional diagnostics
    created_ip = models.GenericIPAddressField(null=True, blank=True)
    created_user_agent = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Email verify token for {self.user.email}"

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @property
    def is_consumed(self) -> bool:
        return self.consumed_at is not None

    @property
    def is_valid(self) -> bool:
        return (not self.is_consumed) and (not self.is_expired)

    def mark_consumed(self, commit: bool = True):
        self.consumed_at = timezone.now()
        if commit:
            self.save(update_fields=["consumed_at"])

    class Meta:
        indexes = [
            models.Index(fields=["user", "expires_at"]),
            models.Index(fields=["token"]),
        ]


class PasswordResetToken(models.Model):
    """
    Tokens for password reset flow.
    - UUID token
    - Expiry + consumed tracking
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="password_reset_tokens"
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)

    # Optional diagnostics
    created_ip = models.GenericIPAddressField(null=True, blank=True)
    created_user_agent = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Password reset token for {self.user.email}"

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @property
    def is_consumed(self) -> bool:
        return self.consumed_at is not None

    @property
    def is_valid(self) -> bool:
        return (not self.is_consumed) and (not self.is_expired)

    def mark_consumed(self, commit: bool = True):
        self.consumed_at = timezone.now()
        if commit:
            self.save(update_fields=["consumed_at"])

    class Meta:
        indexes = [
            models.Index(fields=["user", "expires_at"]),
            models.Index(fields=["token"]),
        ]
