from rest_framework import serializers
from .models import Event, EventRSVP


class EventSerializer(serializers.ModelSerializer):
    rsvp_count = serializers.SerializerMethodField()
    is_rsvped = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'start_datetime',
            'end_datetime', 'location', 'category', 'poster',
            'rsvp_count', 'is_rsvped',
        ]

    def get_rsvp_count(self, obj):
        return obj.rsvps.count()

    def get_is_rsvped(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.rsvps.filter(student=request.user).exists()
        return False
