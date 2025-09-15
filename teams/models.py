import uuid
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.text import slugify
from django.conf import settings
from users.models import User


class Organization(models.Model):
    """
    Tenancy boundary. All teams, roles, and projects live under an org.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="owned_organizations"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["slug"]),
        ]
        constraints = [
            UniqueConstraint(fields=["name"], name="org_name_unique_global")
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:200]
            # basic disambiguation; DB-level unique keeps it safe
            self.slug = base
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Team(models.Model):
    """
    A team belongs to an organization.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="teams")
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    is_archived = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_teams"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("org", "name"),)  # name unique within org
        indexes = [
            models.Index(fields=["org", "name"]),
            models.Index(fields=["is_archived"]),
        ]

    def __str__(self):
        return f"{self.org.name} / {self.name}"


class Role(models.Model):
    """
    Org-scoped role definition (distinct from Django Groups).
    Use for team/project scoping without touching global RBAC.
    Example names: 'Owner', 'Manager', 'Member', 'Viewer'.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="roles")
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    is_system = models.BooleanField(
        default=False
    )  # seed defaults; protect from edits/deletes if you want

    class Meta:
        unique_together = (("org", "name"),)  # same role name can exist in different orgs
        indexes = [
            models.Index(fields=["org", "name"]),
        ]

    def __str__(self):
        return f"{self.org.name} / {self.name}"


class TeamMembership(models.Model):
    """
    Users <-> Teams (with an optional org-scoped Role).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="team_memberships")
    role = models.ForeignKey(
        Role, on_delete=models.SET_NULL, null=True, blank=True, related_name="memberships"
    )

    invited_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="team_invites_sent"
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = (("team", "user"),)  # 1 active membership per team/user
        indexes = [
            models.Index(fields=["team", "user"]),
            models.Index(fields=["user"]),
            models.Index(fields=["role"]),
        ]

    def __str__(self):
        role_name = self.role.name if self.role else "Member"
        return f"{self.user.username} in {self.team.name} as {role_name}"
