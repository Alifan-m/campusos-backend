from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import MapLocation
from .serializers import MapLocationSerializer


class MapLocationListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        locations = MapLocation.objects.all()
        location_type = request.query_params.get('type')
        if location_type:
            locations = locations.filter(location_type=location_type)
        return Response(MapLocationSerializer(locations, many=True).data)
