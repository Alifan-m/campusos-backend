from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['phone_number', 'full_name', 'student_id', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['phone_number', 'full_name', 'student_id']
    ordering = ['-date_joined']
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'student_id', 'course', 'year_of_study', 'profile_picture')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'full_name', 'student_id', 'password1', 'password2'),
        }),
    )
