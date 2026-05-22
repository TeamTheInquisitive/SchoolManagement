import random
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import User, OTP
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    ChangePasswordSerializer, ForgotPasswordSerializer,
    ResetPasswordSerializer, VerifyEmailSerializer,
)


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(user, otp_code, purpose):
    subject = 'Email Verification OTP' if purpose == 'email_verify' else 'Password Reset OTP'
    message = f'Your OTP is: {otp_code}. It expires in {settings.OTP_EXPIRY_MINUTES} minutes.'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


def set_auth_cookies(response, user):
    """Set httpOnly secure cookies for JWT tokens."""
    tokens = RefreshToken.for_user(user)
    access_token = str(tokens.access_token)
    refresh_token = str(tokens)

    # httpOnly cookie - JS cannot access these
    response.set_cookie(
        'access_token', access_token,
        httponly=True,
        secure=not settings.DEBUG,  # secure=True in production (HTTPS)
        samesite='Lax',
        max_age=60 * 60,  # 1 hour
        path='/',
    )
    response.set_cookie(
        'refresh_token', refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite='Lax',
        max_age=7 * 24 * 60 * 60,  # 7 days
        path='/api/v1/auth/',  # only sent to auth endpoints
    )
    return response


def clear_auth_cookies(response):
    response.delete_cookie('access_token', path='/')
    response.delete_cookie('refresh_token', path='/api/v1/auth/')
    return response


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        otp_code = generate_otp()
        OTP.objects.create(user=user, code=otp_code, purpose='email_verify')
        send_otp_email(user, otp_code, 'email_verify')

        response = Response({
            'user': UserSerializer(user).data,
            'message': 'Registration successful. Please verify your email.',
        }, status=status.HTTP_201_CREATED)
        return set_auth_cookies(response, user)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        if request.school and user.school != request.school:
            return Response({'error': 'User does not belong to this school'},
                          status=status.HTTP_403_FORBIDDEN)

        response = Response({
            'user': UserSerializer(user).data,
            'message': 'Login successful',
        })
        return set_auth_cookies(response, user)


class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                pass
        response = Response({'message': 'Logged out'}, status=status.HTTP_200_OK)
        return clear_auth_cookies(response)


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'No refresh token'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            token = RefreshToken(refresh_token)
            response = Response({'message': 'Token refreshed'})
            response.set_cookie(
                'access_token', str(token.access_token),
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=60 * 60,
                path='/',
            )
            # Rotate refresh token
            token.blacklist()
            new_refresh = RefreshToken.for_user(token.payload.get('user_id') and User.objects.get(id=token.payload['user_id']))
            response.set_cookie(
                'refresh_token', str(new_refresh),
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=7 * 24 * 60 * 60,
                path='/api/v1/auth/',
            )
            return response
        except TokenError:
            response = Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)
            return clear_auth_cookies(response)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Wrong password'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password changed successfully'})


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=serializer.validated_data['email'])
            otp_code = generate_otp()
            OTP.objects.create(user=user, code=otp_code, purpose='password_reset')
            send_otp_email(user, otp_code, 'password_reset')
        except User.DoesNotExist:
            pass
        return Response({'message': 'If the email exists, an OTP has been sent'})


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = User.objects.get(email=data['email'])
            expiry = timezone.now() - timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
            otp = OTP.objects.filter(
                user=user, code=data['otp'], purpose='password_reset',
                is_used=False, created_at__gte=expiry
            ).first()
            if not otp:
                return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
            otp.is_used = True
            otp.save()
            user.set_password(data['new_password'])
            user.save()
            return Response({'message': 'Password reset successful'})
        except User.DoesNotExist:
            return Response({'error': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        expiry = timezone.now() - timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
        otp = OTP.objects.filter(
            user=user, code=serializer.validated_data['otp'],
            purpose='email_verify', is_used=False, created_at__gte=expiry
        ).first()
        if not otp:
            return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
        otp.is_used = True
        otp.save()
        user.is_email_verified = True
        user.save()
        return Response({'message': 'Email verified successfully'})


class ResendOTPView(APIView):
    def post(self, request):
        purpose = request.data.get('purpose', 'email_verify')
        otp_code = generate_otp()
        OTP.objects.create(user=request.user, code=otp_code, purpose=purpose)
        send_otp_email(request.user, otp_code, purpose)
        return Response({'message': 'OTP sent successfully'})
