from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import MenuCategory, MenuItem, Order
from .serializers import (
    MenuCategorySerializer, MenuItemSerializer,
    OrderCreateSerializer, OrderSerializer
)


class MenuCategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = MenuCategory.objects.all()
        return Response(MenuCategorySerializer(categories, many=True).data)


class MenuItemListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        items = MenuItem.objects.filter(is_available=True)
        category_id = request.query_params.get('category')
        if category_id:
            items = items.filter(category_id=category_id)
        return Response(MenuItemSerializer(items, many=True).data)


class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderCreateSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            order = serializer.save()
            return Response(
                OrderSerializer(order).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, student=request.user)
            return Response(OrderSerializer(order).data)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=404)


class OrderStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        if not request.user.is_cafeteria_staff:
            return Response({'error': 'Permission denied.'}, status=403)
        try:
            order = Order.objects.get(pk=pk)
            new_status = request.data.get('status')
            valid = ['pending', 'paid', 'preparing', 'ready', 'completed', 'cancelled']
            if new_status not in valid:
                return Response({'error': 'Invalid status.'}, status=400)

            old_status = order.status
            order.status = new_status
            order.save()

            # Release reserved stock when cancelled
            if new_status == 'cancelled' and old_status != 'cancelled':
                for item in order.items.all():
                    if item.menu_item.stock_quantity > 0:
                        MenuItem.objects.filter(id=item.menu_item.id).update(
                            reserved_quantity=max(
                                0,
                                item.menu_item.reserved_quantity - item.quantity
                            )
                        )

            return Response(OrderSerializer(order).data)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=404)
