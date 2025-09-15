from django.urls import path
from .views import SignupView, LoginView, VerifyEmailView, ResendVerificationView


from rest_framework.routers import DefaultRouter
from .views import UserAdminViewSet

app_name = "users"

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/",  LoginView.as_view(), name="login"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path("resend-verification/", ResendVerificationView.as_view(), name="resend-verification"),
]


router = DefaultRouter()
router.register(r"admin/users", UserAdminViewSet, basename="admin-users")
urlpatterns += router.urls
