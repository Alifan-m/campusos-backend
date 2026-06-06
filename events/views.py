from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from .models import Event, EventRSVP
from .serializers import EventSerializer


class EventListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        events = Event.objects.all().order_by('start_datetime')
        category = request.query_params.get('category')
        upcoming = request.query_params.get('upcoming')
        if category:
            events = events.filter(category=category)
        if upcoming == 'true':
            events = events.filter(start_datetime__gte=timezone.now())
        return Response(EventSerializer(events, many=True, context={'request': request}).data)


class EventDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            event = Event.objects.get(pk=pk)
            return Response(EventSerializer(event, context={'request': request}).data)
        except Event.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)


class EventRSVPToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            event = Event.objects.get(pk=pk)
            rsvp, created = EventRSVP.objects.get_or_create(
                event=event, student=request.user
            )
            if not created:
                rsvp.delete()
                return Response({'rsvped': False})
            return Response({'rsvped': True})
        except Event.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
