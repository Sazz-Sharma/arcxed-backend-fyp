from rest_framework import serializers
# from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import User

# User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'is_active')
        
        
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email','username','username_slug', 'is_active', 'date_joined')
        read_only_fields = ('id','email', 'is_active', 'date_joined')
        
    def validate_username_slug(self, value):
        request_user = self.instance
        if request_user.username_slug != value:  # Only validate if changing
            if User.objects.filter(username_slug=value).exists():
                raise serializers.ValidationError("This username_slug is already taken.")
        return value

# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, validators=[validate_password])
#     password2 = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ('email', 'password', 'password2', 'first_name', 'last_name')

#     def validate(self, attrs):
#         if attrs['password'] != attrs['password2']:
#             raise serializers.ValidationError({"password": "Passwords don't match"})
#         return attrs

#     def create(self, validated_data):
#         validated_data.pop('password2')
#         # print(**validated_data)
#         try:
#             user = User.objects.create_user(**validated_data)
#         except:
#             raise serializers.ValidationError({"error": "Email is already in use"})
#         return user

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    
class InitiateRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return attrs

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(min_length=6, max_length=6)
