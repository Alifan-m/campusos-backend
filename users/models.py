from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


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
