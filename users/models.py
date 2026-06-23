from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import random


class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('Phone number is required')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('role', 'super_admin')
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('cafeteria_staff', 'Cafeteria Staff'),
        ('notice_admin', 'Notice/Events Admin'),
        ('super_admin', 'Super Admin'),
    ]

    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)
    full_name = models.CharField(max_length=150)
    student_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    course = models.CharField(max_length=100, blank=True)
    year_of_study = models.IntegerField(null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    profile_picture = models.URLField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    # Password reset
    reset_code = models.CharField(max_length=6, blank=True, null=True)
    reset_code_expires = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name']

    objects = UserManager()

    def __str__(self):
        return f'{self.full_name} ({self.phone_number})'

    @property
    def is_cafeteria_staff(self):
        return self.role in ('cafeteria_staff', 'super_admin')

    @property
    def is_notice_admin(self):
        return self.role in ('notice_admin', 'super_admin')

    @property
    def is_super_admin(self):
        return self.role == 'super_admin'

    def generate_reset_code(self):
        code = ''.join(random.choices('0123456789', k=6))
        self.reset_code = code
        self.reset_code_expires = timezone.now() + timezone.timedelta(minutes=10)
        self.save(update_fields=['reset_code', 'reset_code_expires'])
        return code

    def verify_reset_code(self, code):
        if not self.reset_code or not self.reset_code_expires:
            return False
        if timezone.now() > self.reset_code_expires:
            return False
        return self.reset_code == code

    def clear_reset_code(self):
        self.reset_code = None
        self.reset_code_expires = None
        self.save(update_fields=['reset_code', 'reset_code_expires'])
