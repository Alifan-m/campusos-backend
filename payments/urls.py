from django.urls import path
from .views import InitiateMpesaView, MpesaCallbackView, MpesaStatusView

urlpatterns = [
    path('mpesa/initiate/', InitiateMpesaView.as_view(), name='mpesa-initiate'),
    path('mpesa/callback/', MpesaCallbackView.as_view(), name='mpesa-callback'),
    path('mpesa/status/<str:checkout_request_id>/', MpesaStatusView.as_view(), name='mpesa-status'),
]
