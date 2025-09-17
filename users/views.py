
from rest_framework import generics, viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    UserListSerializer,
    SignupSerializer,
    VerifyEmailSerializer,
    ResendVerificationSerializer,
    LoginTokenObtainPairSerializer,
)


from django.contrib.auth import get_user_model
User = get_user_model()

class IsAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)

class UserAdminViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("email")
    serializer_class = UserListSerializer
    permission_classes = [IsAdminOnly]
    http_method_names = ["get","delete","head","options"]  # list/retrieve/delete





class SignupView(generics.CreateAPIView):
    """
    POST /api/users/signup/
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = SignupSerializer


class VerifyEmailView(APIView):
    """
    GET or POST /api/users/verify-email/?token=...
    Body alternative: {"token": "..."}
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        token = request.query_params.get("token")
        serializer = VerifyEmailSerializer(data={"token": token})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"detail": "Email verified", "user_id": str(user.id)})

    def post(self, request, *args, **kwargs):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"detail": "Email verified", "user_id": str(user.id)})


class ResendVerificationView(generics.CreateAPIView):
    """
    POST /api/users/resend-verification/
    Body: {"email": "user@example.com"}
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = ResendVerificationSerializer


class LoginView(TokenObtainPairView):
    """
    POST /api/users/login/
    Body: {"username": "<email or username>", "password": "..."}
    Returns: {"refresh": "...", "access": "...", "user": {...}}
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginTokenObtainPairSerializer
