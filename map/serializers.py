from rest_framework import serializers
from .models import MapLocation


class MapLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapLocation
        fields = [
            'id', 'name', 'location_type', 'description',
            'location_x', 'location_y',
        ]
