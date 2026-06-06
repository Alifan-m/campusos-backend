from django.urls import path
from .views import MenuCategoryListView, MenuItemListView, OrderCreateView, OrderDetailView, OrderStatusUpdateView

urlpatterns = [
    path('categories/', MenuCategoryListView.as_view(), name='menu-categories'),
    path('menu/', MenuItemListView.as_view(), name='menu-items'),
    path('orders/', OrderCreateView.as_view(), name='orders'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/status/', OrderStatusUpdateView.as_view(), name='order-status'),
]
