from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from users.firebase_helpers import firebase_config
from firebase_admin import auth

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password, role='user', **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have an username')
        
        email = self.normalize_email(email=email)
        user = self.model(username=username, email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # Tạo user trên Firebase Authentication
        firebase_config()
        try:
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name=username
            )

            # Gán custom claims cho admin
            auth.set_custom_user_claims(user_record.uid, {'role': 'admin'})
        except Exception as e:
            print(f"Firebase error during superuser creation: {e}")
            raise ValueError("Không thể tạo tài khoản Firebase.")

        # Tạo user trong Django
        return self.create_user(username=username, email=email, password=password, role='admin', **extra_fields)
        
   
# User
# - id: firebase, PK (token) -> dùng token của firebase (update)
# - username: string, unique
# - email: string, unique
# - password: string, hashed
# - role: string, [admin, user]
# - create_at:  datetime
        
class MyUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    id = models.CharField(max_length=255, primary_key=True)
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    created_at = models.DateTimeField(default=timezone.now)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    
    def __str__(self):
        return self.email



