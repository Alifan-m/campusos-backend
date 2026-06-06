from django.contrib import admin
from .models import MapLocation


@admin.register(MapLocation)
class MapLocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'location_type', 'location_x', 'location_y', 'is_active']
    list_filter = ['location_type', 'is_active']
