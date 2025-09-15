from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import OrganizationViewSet, TeamViewSet, RoleViewSet

router = DefaultRouter()
router.register(r"organizations", OrganizationViewSet, basename="organization")
router.register(r"teams", TeamViewSet, basename="team")
router.register(r"roles", RoleViewSet, basename="role")

urlpatterns = [
    path("", include(router.urls)),
]
