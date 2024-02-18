from django.conf import settings
from rest_framework.response import Response
from rest_framework import status

import requests
import json

MERCHANT_ID = settings.MERCHANT

ZP_API_REQUEST = settings.ZP_API_REQUEST
ZP_API_VERIFY = settings.ZP_API_VERIFY
ZP_API_STARTPAY = settings.ZP_API_STARTPAY
CALL_BACK_URL = settings.CALL_BACK_URL


def sent_payment_request(request_data):
    data = {
        "MerchantID": MERCHANT_ID,
        "CallbackURL": CALL_BACK_URL,
        **request_data
    }
    headers = {'content-type': 'application/json', 'content-length': str(len(data))}
    try:
        response = requests.post(ZP_API_REQUEST, data=json.dumps(data), headers=headers, timeout=10)
        if response.status_code == 200:
            response = response.json()
            if response['Status'] == 100:
                return Response(data={
                    'status': 'success',
                    'url': ZP_API_STARTPAY + str(response['Authority']),
                    'authority': response['Authority']
                }, status=status.HTTP_200_OK)
            else:
                return Response(data={'error_code': str(response['Status'])}, status=status.HTTP_406_NOT_ACCEPTABLE)
        return response

    except requests.exceptions.Timeout:
        return Response(status=status.HTTP_504_GATEWAY_TIMEOUT)
    except requests.exceptions.ConnectionError:
        return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)
