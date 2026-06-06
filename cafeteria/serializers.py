from rest_framework import serializers
from .models import MenuCategory, MenuItem, Order, OrderItem


class MenuCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuCategory
        fields = ['id', 'name', 'description']


class MenuItemSerializer(serializers.ModelSerializer):
    is_in_stock = serializers.ReadOnlyField()
    effective_stock = serializers.ReadOnlyField()

    class Meta:
        model = MenuItem
        fields = [
            'id', 'name', 'description', 'price', 'category',
            'image', 'is_available', 'is_in_stock', 'effective_stock',
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'menu_item_name', 'quantity', 'unit_price', 'subtotal']


class OrderCreateSerializer(serializers.Serializer):
    items = serializers.ListField(
        child=serializers.DictField()
    )

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError('Order must have at least one item.')

        validated = []
        for item_data in items:
            menu_item_id = item_data.get('menu_item')
            quantity = item_data.get('quantity', 1)

            try:
                menu_item = MenuItem.objects.get(id=menu_item_id)
            except MenuItem.DoesNotExist:
                raise serializers.ValidationError(f'Menu item {menu_item_id} not found.')

            if not menu_item.is_available:
                raise serializers.ValidationError(f'{menu_item.name} is not available.')

            if menu_item.stock_quantity > 0:
                if menu_item.effective_stock < quantity:
                    available = menu_item.effective_stock
                    if available == 0:
                        raise serializers.ValidationError(
                            f'{menu_item.name} is sold out.'
                        )
                    raise serializers.ValidationError(
                        f'Only {available} portion(s) of {menu_item.name} left.'
                    )

            validated.append({'menu_item': menu_item, 'quantity': quantity})
        return validated

    def create(self, validated_data):
        from django.db import transaction
        items = validated_data['items']
        student = self.context['request'].user

        with transaction.atomic():
            total = sum(
                item['menu_item'].price * item['quantity']
                for item in items
            )
            order = Order.objects.create(student=student, total_amount=total)

            for item_data in items:
                menu_item = item_data['menu_item']
                quantity = item_data['quantity']

                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=quantity,
                    unit_price=menu_item.price,
                )

                # Reserve stock
                if menu_item.stock_quantity > 0:
                    MenuItem.objects.filter(id=menu_item.id).update(
                        reserved_quantity=menu_item.reserved_quantity + quantity
                    )

            order.generate_pickup_code()
        return order


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'status', 'total_amount', 'created_at',
            'pickup_code', 'items', 'notes',
        ]
