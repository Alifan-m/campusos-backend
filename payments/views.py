from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from cafeteria.models import Order
from .models import MpesaTransaction
from .daraja import DarajaClient


class InitiateMpesaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')
        phone_number = request.data.get('phone_number')

        if not order_id or not phone_number:
            return Response(
                {'error': 'order_id and phone_number are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order = Order.objects.get(id=order_id, student=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        if order.status != 'pending':
            return Response({'error': 'Order is not pending'}, status=status.HTTP_400_BAD_REQUEST)

        if hasattr(order, 'mpesa_transaction'):
            existing = order.mpesa_transaction
            if existing.status == 'success':
                return Response({'error': 'Order already paid'}, status=status.HTTP_400_BAD_REQUEST)
            existing.delete()

        daraja = DarajaClient()
        result = daraja.stk_push(phone_number, order.total_amount, order.id)

        if result.get('ResponseCode') == '0':
            transaction = MpesaTransaction.objects.create(
                order=order,
                phone_number=phone_number,
                amount=order.total_amount,
                checkout_request_id=result['CheckoutRequestID'],
                merchant_request_id=result['MerchantRequestID'],
            )
            return Response({
                'message': 'STK push sent. Check your phone.',
                'checkout_request_id': transaction.checkout_request_id
            }, status=status.HTTP_200_OK)

        return Response(
            {'error': 'Failed to initiate payment', 'details': result},
            status=status.HTTP_400_BAD_REQUEST
        )


class MpesaCallbackView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data.get('Body', {}).get('stkCallback', {})
        checkout_request_id = data.get('CheckoutRequestID')
        result_code = str(data.get('ResultCode', ''))
        result_desc = data.get('ResultDesc', '')

        try:
            transaction = MpesaTransaction.objects.get(checkout_request_id=checkout_request_id)
        except MpesaTransaction.DoesNotExist:
            return Response({'ResultCode': 0, 'ResultDesc': 'Accepted'})

        transaction.result_code = result_code
        transaction.result_description = result_desc

        if result_code == '0':
            items = data.get('CallbackMetadata', {}).get('Item', [])
            for item in items:
                if item.get('Name') == 'MpesaReceiptNumber':
                    transaction.mpesa_receipt_number = item.get('Value', '')
            transaction.status = 'success'
            transaction.order.status = 'paid'
            transaction.order.save()
        else:
            transaction.status = 'failed'

        transaction.save()
        return Response({'ResultCode': 0, 'ResultDesc': 'Accepted'})


class MpesaStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, checkout_request_id):
        try:
            transaction = MpesaTransaction.objects.get(
                checkout_request_id=checkout_request_id,
                order__student=request.user
            )
        except MpesaTransaction.DoesNotExist:
            return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'status': transaction.status,
            'mpesa_receipt_number': transaction.mpesa_receipt_number,
            'amount': transaction.amount,
            'order_status': transaction.order.status
        })
