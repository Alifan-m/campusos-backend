from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['full_name', 'phone_number', 'student_id', 'role', 'is_verified', 'date_joined']
    list_filter = ['role', 'is_verified']
    list_editable = ['is_verified', 'role']
    search_fields = ['full_name', 'phone_number', 'student_id']
    ordering = ['-date_joined']
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('full_name', 'student_id', 'course', 'year_of_study', 'profile_picture')}),
        ('Permissions', {'fields': ('role', 'is_verified', 'is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'full_name', 'student_id', 'role', 'is_verified', 'password1', 'password2'),
        }),
    )
