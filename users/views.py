from pyotp import OTP
from rest_framework import generics, status, permissions
from django.db import transaction
from django.contrib.auth import get_user_model, login
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.utils import timezone
import random
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

from .models import CustomUser




from .serializers import (
    OTPLoginSerializer,
    ResendOTPSerializer,
    
    UserSignupSerializer,
    UserLoginSerializer,
    OTPVerificationSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    UserSerializer,
)

User = get_user_model()

EMAIL_HOST_USER = settings.EMAIL_HOST_USER

# ✅ User Signup View (Registers user & sends OTP)
class UserSignupView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = UserSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save(is_active=False)  # Make user inactive until OTP is verified
        otp = user.generate_otp()
        user.send_otp_email()

        return Response({
            "message": "User registered successfully. Check your email for the OTP."
        }, status=status.HTTP_201_CREATED)
    

# ✅ User Login with OTP (NEW ENDPOINT)
class OTPLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)  # JWT Token Generate
            return Response({
                "message": "Login successful",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ User Login (Only if OTP verified)
class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            if not user.is_active:
                return Response({"error": "Please verify your OTP before logging in."}, status=status.HTTP_403_FORBIDDEN)

            token, created = Token.objects.get_or_create(user=user)
            login(request, user)
            return Response({"token": token.key, "message": "Login successful"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SendOTPView(APIView):
    permission_classes = [AllowAny] 
    def post(self, request):
        email = request.data.get("email")
        user = User.objects.filter(email=email).first()
        
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        user.generate_otp()
        user.send_otp_email()
        return Response({"message": "OTP sent to registered email"}, status=status.HTTP_200_OK)
    

# ✅ OTP Verification (Activates user)
class OTPVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.is_active = True
            user.otp = None  # Clear OTP after verification
            user.save()

            # Generate authentication token after OTP verification
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                "message": "OTP verified successfully",
                "token": token.key
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ Change Password
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ Forgot Password (Sends OTP)
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ Reset Password
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ User Detail View
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user




# ✅ Resend OTP
class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")  # ✅ Safe way to get email
        if not email:
            return Response({"error": "Email field is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        otp_instance, created = CustomUser.objects.get_or_create(email=user.email)
        otp_instance.otp = str(random.randint(100000, 999999))
        otp_instance.created_at = timezone.now()
        otp_instance.expires_at = otp_instance.created_at + timezone.timedelta(minutes=5)
        otp_instance.save()

        print(f"OTP for {user.email}: {otp_instance.otp}")

        return Response({"message": "New OTP sent successfully!"}, status=status.HTTP_200_OK)
