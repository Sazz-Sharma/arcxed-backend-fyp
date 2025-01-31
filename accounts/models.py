from django.db import models

# Create your models here.

from django.core.validators import MinLengthValidator
import random
from datetime import datetime, timedelta
from django.utils import timezone 
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.text import slugify


class OTPVerification(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6, validators=[MinLengthValidator(6)])
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.otp:
            self.otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        if not self.expires_at:
            self.expires_at =  timezone.now()  + timedelta(minutes=10)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return  timezone.now()  > self.expires_at
    



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, username=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, username=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, username, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)  # Display name, NOT unique
    username_slug = models.SlugField(unique=True, blank=True, null=True)  # Unique slug for username
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"  # Use email as the unique identifier
    REQUIRED_FIELDS = ["username"]  # Username is required but not unique

    def __str__(self):
        return self.email
