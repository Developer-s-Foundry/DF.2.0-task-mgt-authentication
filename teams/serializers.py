from rest_framework import serializers
from .models import Organization, Team, Role, TeamMembership
from users.models import User


class OrganizationSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Organization
        fields = ("id", "name", "slug", "owner", "created_at")
        read_only_fields = ("id", "slug", "owner", "created_at")

    def create(self, validated_data):
        org = Organization.objects.create(owner=self.context["request"].user, **validated_data)
        # (Optional) seed system roles here if you didn’t do it via signals
        for r in ["Owner", "Manager", "Member", "Viewer"]:
            Role.objects.get_or_create(org=org, name=r, defaults={"is_system": True})
        return org


class TeamSerializer(serializers.ModelSerializer):
    org = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all())
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Team
        fields = ("id", "org", "name", "description", "is_archived", "created_by", "created_at", "updated_at")
        read_only_fields = ("id", "created_by", "created_at", "updated_at")

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("id", "org", "name", "description", "is_system")
        read_only_fields = ("id", "is_system")


class TeamMembershipSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    team = serializers.PrimaryKeyRelatedField(queryset=Team.objects.all())
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), allow_null=True, required=False)

    class Meta:
        model = TeamMembership
        fields = ("id", "team", "user", "role", "invited_by", "joined_at", "left_at")
        read_only_fields = ("id", "invited_by", "joined_at", "left_at")

    def create(self, validated_data):
        validated_data["invited_by"] = self.context["request"].user
        return super().create(validated_data)
