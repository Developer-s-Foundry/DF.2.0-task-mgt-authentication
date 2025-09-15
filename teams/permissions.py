from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Organization, Team, TeamMembership, Role

def _is_org_owner(user, org: Organization) -> bool:
    return org and org.owner_id == user.id

def _team_membership(user, team: Team):
    if not user or not team:
        return None
    return TeamMembership.objects.select_related("role").filter(team=team, user=user, left_at__isnull=True).first()

def _has_team_role(user, team: Team, allowed: set[str]) -> bool:
    m = _team_membership(user, team)
    return bool(m and m.role and m.role.name in allowed)

class IsOrgOwnerOrReadOnly(BasePermission):
    """Org owner can write; others can read."""
    def has_object_permission(self, request, view, obj: Organization):
        if request.method in SAFE_METHODS:
            return True
        return _is_org_owner(request.user, obj)

class IsTeamReadable(BasePermission):
    """Team is readable by org owner or any team member; writes limited below."""
    def has_object_permission(self, request, view, team: Team):
        if request.method in SAFE_METHODS:
            return _is_org_owner(request.user, team.org) or _team_membership(request.user, team)
        return True  # defer to write permission class

class TeamWriteByOwnerOrManager(BasePermission):
    """
    Allow create/update/delete if:
      - user is the org owner, OR
      - user has team role in {'Owner','Manager'}
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, team: Team):
        if _is_org_owner(request.user, team.org):
            return True
        return _has_team_role(request.user, team, {"Owner", "Manager"})
