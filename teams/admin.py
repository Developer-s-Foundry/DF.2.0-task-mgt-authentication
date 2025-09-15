from django.contrib import admin
from .models import Organization, Team, Role, TeamMembership


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "owner", "created_at")
    search_fields = ("name", "slug", "owner__username", "owner__email")
    list_filter = ("created_at",)
    ordering = ("name",)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "org", "created_by", "is_archived", "created_at", "updated_at")
    search_fields = ("name", "org__name", "created_by__username")
    list_filter = ("is_archived", "created_at", "updated_at", "org")
    ordering = ("org", "name")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "org", "description", "is_system")
    search_fields = ("name", "org__name")
    list_filter = ("is_system", "org")
    ordering = ("org", "name")


@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "team", "role", "invited_by", "joined_at", "left_at")
    search_fields = (
        "user__username", "user__email", "team__name", "role__name", "invited_by__username"
    )
    list_filter = ("role", "joined_at", "left_at", "team__org")
    ordering = ("team", "user")
