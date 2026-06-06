from django.contrib import admin
from .models import Event, EventRSVP


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'location', 'start_datetime', 'is_published']
    list_filter = ['category', 'is_published']
    search_fields = ['title']


@admin.register(EventRSVP)
class EventRSVPAdmin(admin.ModelAdmin):
    list_display = ['event', 'student', 'created_at']
