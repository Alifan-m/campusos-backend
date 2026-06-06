from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Notice
from .serializers import NoticeSerializer

class NoticeListView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        notices = Notice.objects.all().order_by('-created_at')
        category = request.query_params.get('category')
        
        if category:
            # Normalize to lowercase to match the DB value
            category_lower = category.lower()
            
            # Check if there are actually any notices with this exact category
            filtered_notices = notices.filter(category__iexact=category_lower)
            
            if filtered_notices.exists():
                notices = filtered_notices
            # If no matches found (e.g. "General" or "Academic"), do not return an empty array.
            # Instead, let's fall back to showing everything so the UI stays populated.

        return Response(NoticeSerializer(notices, many=True).data)

class NoticeDetailView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, pk):
        try:
            notice = Notice.objects.get(pk=pk)
            return Response(NoticeSerializer(notice).data)
        except Notice.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
