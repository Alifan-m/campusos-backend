from rest_framework import serializers
from .models import Notice


class NoticeSerializer(serializers.ModelSerializer):
    posted_by = serializers.CharField(
        source='author.full_name', read_only=True
    )
    is_urgent = serializers.SerializerMethodField()

    class Meta:
        model = Notice
        fields = [
            'id', 'title', 'body', 'category',
            'is_urgent', 'created_at', 'posted_by',
        ]

    def get_is_urgent(self, obj):
        return obj.category == 'urgent'
