from django.db.models import Q
from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Organization, Team, Role, TeamMembership
from .serializers import OrganizationSerializer, RoleSerializer, TeamSerializer, TeamMembershipSerializer
from .permissions import IsOrgOwnerOrReadOnly, IsTeamReadable, TeamWriteByOwnerOrManager


class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrgOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        # Orgs where user is owner OR belongs to a team (active membership)
        return (
            Organization.objects
            .filter(
                Q(owner=user) |
                Q(teams__memberships__user=user,
                  teams__memberships__left_at__isnull=True)
            )
            .distinct()
        )


class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeamReadable, TeamWriteByOwnerOrManager]

    def get_queryset(self):
        user = self.request.user
        # Teams in orgs the user owns OR teams where user is a member (active)
        return (
            Team.objects.select_related("org", "created_by")
            .filter(
                Q(org__owner=user) |
                Q(memberships__user=user, memberships__left_at__isnull=True)
            )
            .distinct()
        )

    # ---- Membership operations ----
    @action(detail=True, methods=["get"], url_path="members")
    def members(self, request, pk=None):
        team = self.get_object()
        qs = TeamMembership.objects.select_related("user", "role")\
            .filter(team=team, left_at__isnull=True)
        data = [{
            "id": str(m.id),
            "user_id": str(m.user_id),
            "username": m.user.username,
            "email": m.user.email,
            "role": m.role.name if m.role else None,
            "joined_at": m.joined_at,
        } for m in qs]
        return Response(data)

    @action(detail=True, methods=["post"], url_path="add-member")
    def add_member(self, request, pk=None):
        team = self.get_object()
        self.check_object_permissions(request, team)  # Owner/Manager required

        ser = TeamMembershipSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)

        # enforce membership is for this team
        if ser.validated_data["team"].id != team.id:
            return Response({"detail": "team mismatch"}, status=status.HTTP_400_BAD_REQUEST)

        # enforce role belongs to same org
        role = ser.validated_data.get("role")
        if role and role.org_id != team.org_id:
            return Response({"detail": "role must belong to the same organization"},
                            status=status.HTTP_400_BAD_REQUEST)

        ser.save()
        return Response(ser.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["put", "patch"], url_path="set-role")
    def set_role(self, request, pk=None):
        team = self.get_object()
        self.check_object_permissions(request, team)

        user_id = request.data.get("user")
        role_id = request.data.get("role")  # may be null to clear
        m = get_object_or_404(TeamMembership, team=team, user_id=user_id, left_at__isnull=True)

        role = None
        if role_id:
            role = get_object_or_404(Role, id=role_id, org=team.org)

        m.role = role
        m.save(update_fields=["role"])
        return Response({"detail": "role updated"})

    @action(detail=True, methods=["delete"], url_path="remove-member")
    def remove_member(self, request, pk=None):
        team = self.get_object()
        self.check_object_permissions(request, team)

        user_id = request.query_params.get("user")
        m = get_object_or_404(TeamMembership, team=team, user_id=user_id, left_at__isnull=True)

        # either soft-leave (timestamp) or hard delete — pick a policy
        # m.left_at = timezone.now(); m.save(update_fields=["left_at"])
        m.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class RoleViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Read-only list of roles in an org (filter by ?org=<org_id>)."""
    queryset = Role.objects.select_related("org")
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        org_id = self.request.query_params.get("org")
        if org_id:
            qs = qs.filter(org_id=org_id)
        return qs.order_by("name")
