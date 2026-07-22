from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.MenuCategoryListView.as_view()),
    path('menu/', views.MenuItemListView.as_view()),
    path('orders/', views.OrderCreateView.as_view()),
    path('orders/history/', views.OrderHistoryView.as_view()),
    path('orders/<int:pk>/', views.OrderDetailView.as_view()),
    path('orders/<int:pk>/status/', views.OrderStatusUpdateView.as_view()),
]
