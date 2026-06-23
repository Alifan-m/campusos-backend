from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.conf import settings
from django.core.mail import send_mail
from .serializers import (
    UserSerializer, RegisterSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer,
)

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Registration successful. Your account is pending verification by the university. You will be able to log in once approved.',
                'user': UserSerializer(user).data,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')

        user = authenticate(request, phone_number=phone_number, password=password)

        if not user:
            return Response(
                {'error': 'Invalid phone number or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_verified:
            return Response(
                {'error': 'Your account is pending verification. Please wait for admin approval or contact the university office.'},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.validated_data['phone_number']

        generic_response = {
            'message': 'If that phone number is registered, a reset code has been sent to your email.'
        }

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response(generic_response, status=status.HTTP_200_OK)

        if not user.email:
            # No email on file for this account — can't deliver a code
            # anywhere, so point them to a human instead of silently
            # failing.
            return Response(
                {'message': 'No email is on file for this account. Please contact the university ICT office to reset your password.'},
                status=status.HTTP_200_OK
            )

        code = user.generate_reset_code()

        email_sent = False
        try:
            send_mail(
                subject='CampusOS Password Reset Code',
                message=(
                    f'Your CampusOS password reset code is: {code}\n\n'
                    'This code expires in 10 minutes. If you did not '
                    'request this, you can safely ignore this email.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            email_sent = True
        except Exception as e:
            # SMTP not configured yet, or the send failed for some
            # other reason — fall back to logging it so you can still
            # test locally without email working.
            print(f'[Password Reset] Failed to email {user.email}: {e}')
            print(f'[Password Reset] Code for {phone_number}: {code}')

        if email_sent:
            generic_response['message'] = 'A reset code has been sent to your email.'
        elif settings.DEBUG:
            generic_response['debug_code'] = code

        return Response(generic_response, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.validated_data['phone_number']
        code = serializer.validated_data['code']
        new_password = serializer.validated_data['new_password']

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid phone number or code.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.verify_reset_code(code):
            return Response(
                {'error': 'Invalid or expired reset code.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        user.clear_reset_code()

        return Response(
            {'message': 'Password reset successful. You can now log in with your new password.'},
            status=status.HTTP_200_OK
        )
