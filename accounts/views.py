from django.shortcuts import render
from urllib.parse import urlencode
# Create your views here.
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from .serializers import *
import os
from dotenv import load_dotenv
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from .models import OTPVerification, User
import requests 

load_dotenv()

class GoogleLoginView(APIView):
    
    def get(self, request):
        # Generate Google OAuth2 authorization URL
        params = {
            'response_type': 'code',
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'redirect_uri': 'http://localhost:3000/auth/google/callback',
            'scope': 'email profile',
            'access_type': 'offline',
        }
        authorization_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
        return Response({'authorization_url': authorization_url})
    
    @swagger_auto_schema(
        request_body=GoogleAuthSerializer,
        responses={200: openapi.Response("Access and refresh tokens")},
    )
    def post(self, request):
        # code = request.data.get('code')
        # if not code:
        #     return Response({'error': 'Authorization code is required'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = GoogleAuthSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        code = serializer.validated_data['code']
        try:
            # Exchange code for tokens
            token_response = requests.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'code': code,
                    'client_id': os.getenv('GOOGLE_CLIENT_ID'),
                    'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
                    'redirect_uri': 'http://localhost:3000/auth/google/callback',
                    'grant_type': 'authorization_code',
                }
            )
            token_data = token_response.json()
            print(token_data)
            idinfo = id_token.verify_oauth2_token(token_data['id_token'], google_requests.Request(), os.getenv('GOOGLE_CLIENT_ID'))

            # Proceed with user creation/login
            email = idinfo['email']
            given_name = idinfo.get('given_name', '')
            family_name = idinfo.get('family_name', '')
            username = f"{given_name} {family_name}".strip()

            user, created = User.objects.get_or_create(
                email=email,
                defaults={'username': username}
            )

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
            200: UserDetailSerializer,
            401: "Unauthorized"
        },
        security=[{'Bearer': []}]
    )
    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

class UpdateUserView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Update user profile",
        request_body=UserDetailSerializer,
        responses={
            200: UserSerializer,
            400: "Bad Request",
            401: "Unauthorized"
        },
        security=[{'Bearer': []}]
    )
    def put(self, request):
        serializer = UserDetailSerializer(request.user, data=request.data, partial=True)
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
    
    

# Onboarding view

# class OnboardingView(APIView):
#     permission_classes = [IsAuthenticated]

#     @swagger_auto_schema(
#         operation_description="Complete user onboarding",
#         request_body=openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             properties={
#                 'username_slug': openapi.Schema(type=openapi.TYPE_STRING, description='Unique username slug')
#             },
#             required=['username_slug']
#         ),
#         responses={
#             200: "Onboarding completed successfully",
#             400: "Bad request"
#         }
#     )
#     def post(self, request):
#         username_slug = request.data.get('username_slug')
#         if not username_slug:
#             return Response({'error': 'username_slug is required'}, status=status.HTTP_400_BAD_REQUEST)

#         # Check if the username_slug is unique
#         if User.objects.filter(username_slug=username_slug).exists():
#             return Response({'error': 'username_slug already exists'}, status=status.HTTP_400_BAD_REQUEST)

#         # Update the user's username_slug
#         user = request.user
#         user.username_slug = username_slug
#         user.save(update_fields=['username_slug'])

#         return Response({'message': 'Onboarding completed successfully', 'user': UserDetailSerializer(user).data})
    