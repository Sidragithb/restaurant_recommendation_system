from django.urls import path
from .views import (
    OTPLoginView, SendOTPView, UserSignupView, UserLoginView, OTPVerificationView, ResendOTPView,
    ChangePasswordView, ForgotPasswordView, ResetPasswordView,UserDetailView
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("signup/", UserSignupView.as_view(), name="signup"),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('otp-login/', OTPLoginView.as_view(), name='otp-login'),  # ✅ New OTP-based login
    path("send-otp/", SendOTPView.as_view(), name="send-otp"),\
    path("resend-otp/", ResendOTPView.as_view(), name="resend-otp"),
    path('me/', UserDetailView.as_view(), name='user'),
    path('token-refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path("verify-otp/", OTPVerificationView.as_view(), name="verify-otp"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),


]
