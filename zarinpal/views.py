from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from zarinpal.serializers import PaymentRequestSerializer
from zarinpal.utils import sent_payment_request, verify_payment_request
from api.models import Order, Transaction, User
from api.utils import check_authentication_api, get_user_data
import re
from api.loggers import PaymentApiLogger, TransactionApiLogger


class PaymentRequestView(APIView):
    serializer_class = PaymentRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        TOKEN = request.headers.get('token')
        pattern = r'^[B,b]earer\s([a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+)$'
        # if not TOKEN:
        #     return Response(status=status.HTTP_403_FORBIDDEN)
        # if not re.match(pattern, TOKEN):
        #     return Response(status=status.HTTP_400_BAD_REQUEST)

        # authentication_api = check_authentication_api(request, TOKEN)
        authentication_api = True
        if not serializer.is_valid():
            return Response(data={"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        if authentication_api:
            try:
                user = User.objects.get(oid=serializer.data["user_id"])
            except User.DoesNotExist:
                user_data = get_user_data(serializer.data["user_id"])
                if not user_data:
                    return Response(data={"message": "Invalid user id"}, status=status.HTTP_404_NOT_FOUND)
                user = User.objects.create(
                    username=user_data['username'],
                    oid=serializer.data["user_id"],
                    phone=user_data['phone']
                )
                PaymentApiLogger.info(
                    f"new user created, id:{user.oid}, username: {user.username}, phone: {user.phone}")
            except Exception:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            response = sent_payment_request(serializer.data)
            if response.status_code == 200:
                order = Order.objects.create(status=Order.OrderStats.AWAITING_PAYMENT,
                                             type=serializer.data["type"].upper(),
                                             event_id=serializer.data["event_id"] if serializer.data[
                                                                                         "type"] == "purchase" else None,
                                             Authority=response.data["authority"],
                                             user=user,
                                             amount=serializer.data["amount"],
                                             payment_method=Order.PaymentMethods.BANK)
                PaymentApiLogger.info(
                    f"payment gate successfully requested for user {user.id} ,order_id {order.id} amount: {order.amount}")
                response.data["order_id"] = order.order_id
            else:
                PaymentApiLogger.warning(f"failed to get payment gate for user {user.id} ,err: {response.data}")
            return response


class PaymentVerifyView(APIView):
    def get(self, request):
        authority = request.query_params.get('Authority')
        status = request.query_params.get('Status')
        order = Order.objects.get(Authority=authority)
        response = verify_payment_request(authority=order.Authority, amount=order.amount)

        if response.status_code == 200:
            order.status = Order.OrderStats.COMPLETED
            order.save()
            Transaction.objects.create(order=order, ref_id=response.data["RefID"],
                                       response_code=response.data["Status"])
            response.data["message"] = "payment successful, ref_id: {}".format(response.data["RefID"])
            TransactionApiLogger.info(
                f"transaction successfully done for user {order.user.oid}, order: {order.id}")
            PaymentApiLogger.info(
                f"payment completed for user {order.user.id}, order_id: {order.id}, message: {response.data['status_code_msg']}")
        else:
            order.status = Order.OrderStats.CANCELLED
            PaymentApiLogger.warning(
                f"payment failed for user {order.user.id}, order_id: {order.id} ,err: {response.data['status_code_msg']}")

            order.save()
        return response
