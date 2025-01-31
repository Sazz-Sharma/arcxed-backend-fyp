from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from google.oauth2 import id_token
from google.auth.transport import requests
from .serializers import *
import os
from dotenv import load_dotenv
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from .models import OTPVerification, User

load_dotenv()

class GoogleLoginView(APIView):
    @swagger_auto_schema(
        operation_description="Google OAuth login endpoint",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING, description='Google OAuth token')
            },
            required=['token']
        ),
        responses={
            200: openapi.Response(
                description="Successful login",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: "Invalid token"
        }
    )
    def post(self, request):
        try:
            idinfo = id_token.verify_oauth2_token(
                request.data.get('token'),
                requests.Request(),
                os.getenv('GOOGLE_CLIENT_ID'),
            )
            
            # Check if user exists
            user, created = User.objects.get_or_create(
                email=idinfo['email'],
                defaults={
                    'first_name': idinfo.get('given_name', ''),
                    'last_name': idinfo.get('family_name', ''),
                }
            )

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        except ValueError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    

# class RegisterView(APIView):
#     @swagger_auto_schema(
#         operation_description="Register a new user",
#         request_body=RegisterSerializer,
#         responses={
#             201: UserSerializer,
#             400: "Bad Request"
#         }
#     )
#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             return Response({
#                 "user": UserSerializer(user).data,
#                 "message": "User Created Successfully"
#             }, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class InitiateRegistrationView(APIView):
    @swagger_auto_schema(
        operation_description="Step 1: Initiate user registration and send OTP",
        request_body=InitiateRegistrationSerializer,
        responses={200: "OTP sent successfully", 400: "Bad request"}
    )
    def post(self, request):
        serializer = InitiateRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            # Check if user already exists
            if User.objects.filter(email=email).exists():
                return Response({'error': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Create or update OTP
            otp_obj, _ = OTPVerification.objects.update_or_create(
                email=email,
                defaults={'is_verified': False, 'otp': None, 'expires_at': None}
            )

            # Send OTP email
            send_mail(
                'Your Registration OTP',
                f'Your OTP for registration is: {otp_obj.otp}. Valid for 10 minutes.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            # Store registration data in session
            request.session['registration_data'] = {
                'email': email,
                'username': username,
                'password': password
            }
            request.session.set_expiry(600)  # 10 minutes

            return Response({'message': 'OTP sent successfully. Please verify within 10 minutes.', 'email': email})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPAndRegisterView(APIView):
    @swagger_auto_schema(
        operation_description="Step 2: Verify OTP and complete registration",
        request_body=VerifyOTPSerializer,
        responses={201: UserSerializer, 400: "Bad request", 404: "OTP verification not found"}
    )
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']

            try:
                otp_obj = OTPVerification.objects.get(email=email)
                
                if otp_obj.is_expired:
                    return Response({'error': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)

                if otp_obj.otp != otp:
                    return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

                # Get registration data from session
                registration_data = request.session.get('registration_data')
                if not registration_data:
                    return Response({'error': 'Registration session expired'}, status=status.HTTP_400_BAD_REQUEST)

                # Create user without username_slug (set later)
                user = User.objects.create_user(
                    email=email,
                    username=registration_data['username'],
                    password=registration_data['password']
                )

                otp_obj.is_verified = True
                otp_obj.save()

                del request.session['registration_data']

                return Response({'message': 'Registration completed successfully', 'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)

            except ObjectDoesNotExist:
                return Response({'error': 'OTP verification not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Get current user details",
        responses={
            200: UserSerializer,
            401: "Unauthorized"
        },
        security=[{'Bearer': []}]
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class UpdateUserView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Update user profile",
        request_body=UserSerializer,
        responses={
            200: UserSerializer,
            400: "Bad Request",
            401: "Unauthorized"
        },
        security=[{'Bearer': []}]
    )
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Change user password",
        request_body=ChangePasswordSerializer,
        responses={
            200: "Password changed successfully",
            400: "Bad Request",
            401: "Unauthorized"
        },
        security=[{'Bearer': []}]
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.data.get('old_password')):
                user.set_password(serializer.data.get('new_password'))
                user.save()
                return Response({'message': 'Password changed successfully'})
            return Response({'error': 'Wrong password'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeactivateUserView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Deactivate user account",
        responses={
            200: "User deactivated successfully",
            401: "Unauthorized"
        },
        security=[{'Bearer': []}]
    )
    def post(self, request):
        user = request.user
        user.is_active = False
        user.save()
        return Response({'message': 'User deactivated successfully'})

class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Delete user account",
        responses={
            200: "User deleted successfully",
            401: "Unauthorized"
        },
        security=[{'Bearer': []}]
    )
    def delete(self, request):
        user = request.user
        user.delete()
        return Response({'message': 'User deleted successfully'})

class PasswordResetRequestView(APIView):
    @swagger_auto_schema(
        operation_description="Request password reset email",
        request_body=PasswordResetRequestSerializer,
        responses={
            200: "Password reset email sent if account exists",
            400: "Bad Request"
        }
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                # Generate password reset token
                # Send reset email
                send_mail(
                    'Password Reset',
                    'Here is your password reset link: [link]',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
            return Response({'message': 'Password reset email sent if account exists'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    @swagger_auto_schema(
        operation_description="Confirm password reset with token",
        request_body=PasswordResetConfirmSerializer,
        responses={
            200: "Password reset successfully",
            400: "Bad Request"
        }
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            # Verify token and reset password
            return Response({'message': 'Password reset successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    