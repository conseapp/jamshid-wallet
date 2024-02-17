from django.shortcuts import get_object_or_404

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models import User, Wallet
from api.utils import check_authentication_api, get_user_data

import re


class DepositView(APIView):
    def post(self, request):
        user_id = request.query_params.get('user_id')
        amount = request.query_params.get('amount')
        TOKEN = request.headers.get('token')
        pattern = r'^[B,b]earer\s([a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+)$'
        if not TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if not re.match(pattern, TOKEN):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        authentication_api = check_authentication_api(request, TOKEN)

        if authentication_api:
            user_data = get_user_data(user_id)
            if not user_data:
                return Response(data={"message": "Invalid user id"}, status=status.HTTP_404_NOT_FOUND)
            user_id = user_data['_id']['$oid']
            try:
                user = User.objects.get(oid=user_id)
            except User.DoesNotExist:
                user = User.objects.create(
                    username=user_data['username'],
                    oid=user_id,
                    phone=user_data['phone']
                )
            except Exception:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            result = user.deposit(int(amount))
            return Response(data=result, status=status.HTTP_202_ACCEPTED)

        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class PurchaseView(APIView):
    def post(self, request):
        user_id = request.query_params.get('user_id')
        event_id = request.query_params.get('event_id')
        amount = request.query_params.get('amount')
        TOKEN = request.headers.get('token')
        pattern = r'^[B,b]earer\s([a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+)$'
        if not TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if not re.match(pattern, TOKEN):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        authentication_api = check_authentication_api(request, TOKEN)

        if authentication_api:
            user_data = get_user_data(user_id)
            if not user_data:
                return Response(data={"message": "Invalid user id"}, status=status.HTTP_404_NOT_FOUND)
            user_id = user_data['_id']['$oid']
            try:
                user = User.objects.get(oid=user_id)
            except User.DoesNotExist:
                user = User.objects.create(
                    username=user_data['username'],
                    oid=user_id,
                    phone=user_data['phone']
                )
            except Exception:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            result = user.purchase_event(event_id, int(amount))
            if result:
                data = {
                    "message": f"successfully purchased event {event_id} with amount of {amount} for user {user_id}, new balance is {user.wallet.balance}"}
                return Response(data=data, status=status.HTTP_200_OK)
            else:
                data = {
                    "message": f"Insufficient Funds, your balance: {user.wallet.balance}, event {event_id} price: {amount}"}
                return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class GetUserBalance(APIView):
    def post(self, request):
        user_id = request.query_params.get('user_id')
        TOKEN = request.headers.get('token')
        pattern = r'^[B,b]earer\s([a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+)$'
        if not TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if not re.match(pattern, TOKEN):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        authentication_api = check_authentication_api(request, TOKEN)

        if authentication_api:
            user_data = get_user_data(user_id)
            if not user_data:
                return Response(data={"message": "Invalid user id"}, status=status.HTTP_404_NOT_FOUND)
            user_id = user_data['_id']['$oid']
            user = get_object_or_404(User, oid=user_id)

            return Response(data=user.get_balance(), status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
