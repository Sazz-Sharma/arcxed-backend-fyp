from django.db import models

# Create your models here.

from django.core.validators import MinLengthValidator
import random
from datetime import datetime, timedelta
from django.utils import timezone 

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