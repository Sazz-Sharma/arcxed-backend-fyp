from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import *

from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

urlpatterns = [
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/google/', GoogleLoginView.as_view(), name='google_login'),
    path('auth/user/', UserDetailView.as_view(), name='user_detail'),
    
    #User-Management
    
    path('auth/register/initiate/', InitiateRegistrationView.as_view(), name='register_initiate'),
    path('auth/register/verify/', VerifyOTPAndRegisterView.as_view(), name='register_verify'),
    path('auth/user/', UserDetailView.as_view(), name='user_detail'),
    path('auth/user/update/', UpdateUserView.as_view(), name='user_update'),
    path('auth/user/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('auth/user/deactivate/', DeactivateUserView.as_view(), name='deactivate_user'),
    path('auth/user/delete/', DeleteUserView.as_view(), name='delete_user'),
    
    
    #Password-Reset
     path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
     
]

