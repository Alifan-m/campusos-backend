import requests
import base64
from datetime import datetime
from django.conf import settings


class DarajaClient:

    def _get_access_token(self):
        consumer_key = settings.MPESA_CONSUMER_KEY
        consumer_secret = settings.MPESA_CONSUMER_SECRET
        credentials = base64.b64encode(
            f"{consumer_key}:{consumer_secret}".encode()
        ).decode()
        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(
            url,
            headers={"Authorization": f"Basic {credentials}"}
        )
        return response.json().get("access_token")

    def _get_password(self, timestamp):
        shortcode = settings.MPESA_SHORTCODE
        passkey = settings.MPESA_PASSKEY
        raw = f"{shortcode}{passkey}{timestamp}"
        return base64.b64encode(raw.encode()).decode()

    def _normalize_phone(self, phone):
        phone = str(phone).strip().replace(" ", "")
        if phone.startswith("+254"):
            return phone[1:]
        if phone.startswith("0"):
            return "254" + phone[1:]
        if phone.startswith("254"):
            return phone
        return "254" + phone

    def stk_push(self, phone_number, amount, order_id):
        access_token = self._get_access_token()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = self._get_password(timestamp)
        phone = self._normalize_phone(phone_number)
        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone,
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": f"CampusOS-Order-{order_id}",
            "TransactionDesc": f"Payment for Order #{order_id}"
        }
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        response = requests.post(
            url,
            json=payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )
        return response.json()
