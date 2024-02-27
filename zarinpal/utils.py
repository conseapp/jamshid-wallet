from django.conf import settings
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from dotenv import load_dotenv
import os
import requests
import json
from api.contextmanagers import RedisConnection, RedisConnectioKeys

load_dotenv()

MERCHANT_ID = settings.MERCHANT
ZP_API_REQUEST = settings.ZP_API_REQUEST
ZP_API_VERIFY = settings.ZP_API_VERIFY
ZP_API_STARTPAY = settings.ZP_API_STARTPAY
CALL_BACK_URL = settings.CALL_BACK_URL
ZP_ERROR_CODES = settings.ZP_ERROR_CODES

redis_credentials: RedisConnectioKeys = {
    'host': 'localhost',
    'port': '6379',
    'password': str(os.getenv('REDIS_PASSWORD'))
}


def sent_payment_request(request_data):
    data = {
        "MerchantID": MERCHANT_ID,
        "CallbackURL": CALL_BACK_URL,
        "Amount": request_data["amount"],
        "Description": request_data["description"],
        "Phone": request_data["phone"]
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


def verify_payment_request(authority, amount):
    data = {
        "MerchantID": settings.MERCHANT,
        "Amount": amount,
        "Authority": authority,
    }
    data = json.dumps(data)
    # set content length by data
    headers = {'content-type': 'application/json', 'content-length': str(len(data))}
    try:
        response = requests.post(ZP_API_VERIFY, data=data, headers=headers)
        response = response.json()
        response["status_code_msg"] = ZP_ERROR_CODES.get(response["Status"])
        if response["Status"] == 100 or response["Status"] == 101:
            return Response(data=response, status=status.HTTP_200_OK)
        else:
            return Response(data=response, status=status.HTTP_406_NOT_ACCEPTABLE)

    except requests.exceptions.Timeout:
        return Response(status=status.HTTP_504_GATEWAY_TIMEOUT)
    except requests.exceptions.ConnectionError:
        return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)




def register_mafia_event(event_id, token):
    url = "https://api.mafia.jamshid.app/event/reserve/mock/"
    headers = {'content-type': 'application/json', "Authorization": f"Bearer {token}"}
    timestamp = int(timezone.localtime().timestamp())

    data = r'{"event_id" : "%s","requested_at": %i}' % (event_id, timestamp)
    try:
        response = requests.post(
            url=url,
            headers=headers,
            data=data)
        if response.json()['status'] == 200:
            return Response(response.json()["data"], status=status.HTTP_201_CREATED)
        else:
            return Response(response.json()["data"], status=status.HTTP_400_BAD_REQUEST)

    except requests.exceptions.Timeout:
        return Response(status=status.HTTP_504_GATEWAY_TIMEOUT)
    except requests.exceptions.ConnectionError:
        return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)


def get_user_token(user_id: str, redis_credentials: RedisConnectioKeys):
    with RedisConnection(**redis_credentials, retries=3) as rd:
        key = f"jwt-{user_id}"
        print('in redis connection')
        if rd.exists(key):
            token = rd.get(key)
            print('jwt token exists')

            return Response({"token": token}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "user not logged in"}, status=status.HTTP_404_NOT_FOUND)
