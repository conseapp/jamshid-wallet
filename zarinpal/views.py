from django.shortcuts import render
from django.contrib.humanize.templatetags.humanize import intcomma
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
import re
from zarinpal.serializers import PaymentRequestSerializer
from zarinpal.utils import sent_payment_request, verify_payment_request, register_mafia_event, redis_credentials, \
    get_user_token
from api.models import Order, Transaction, User
from api.utils import check_authentication_api, get_user_data
from api.loggers import PaymentApiLogger, TransactionApiLogger, RegisterEventApiLogger


class PaymentRequestView(APIView):
    serializer_class = PaymentRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        TOKEN = request.headers.get('token')
        pattern = r'^[B,b]earer\s([a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+)$'
        if not TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if not re.match(pattern, TOKEN):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not serializer.is_valid():
            return Response(data={"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        authentication_api = check_authentication_api(request, TOKEN)
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
        else:
            return Response(data={"error": "invalid user token"}, status=status.HTTP_404_NOT_FOUND)


class PaymentVerifyView(APIView):
    def get(self, request):
        authority = request.query_params.get('Authority')
        status = request.query_params.get('Status')
        order = Order.objects.get(Authority=authority)
        response = verify_payment_request(authority=order.Authority, amount=order.amount)

        if response.status_code == 200:
            if order.status == "COMPLETED":
                response.data["message"] = "عملیات پرداخت موفق بوده و قبلا تایید پرداخت انجام شده"
                response.data["status_text"] = "عمیات موفق"
            else:
                order.status = Order.OrderStats.COMPLETED
                order.save()
                Transaction.objects.create(order=order, ref_id=response.data["RefID"],
                                           response_code=response.data["Status"])
                if order.type == "PURCHASE":
                    user_token = get_user_token(order.user.oid, redis_credentials)

                    # r = redis(redis.StrictRedis(host="localhost", port="6379", password=os.environ.get(""),
                    #                           decode_responses=True))
                    print(user_token)
                    if user_token:
                        res = register_mafia_event(order.event_id, user_token.data['token'])
                        if res.status_code == 201:
                            response.data["core-message"] = res.json()
                            response.data["event-name"] = res.json()['data']["event_name"]
                            RegisterEventApiLogger.info('successfully registered event in jamshid core db')
                        else:
                            response.data["core-message"] = "failed to register event in core db"
                    response.data["message"] = f"رزرو ایونت {order.event_id} با موفقیت انجام شد"
                    response.data["event_id"] = order.event_id
                elif order.type == "DEPOSIT":
                    response.data["message"] = f"مبلغ {intcomma(order.amount)} تومان به حساب شما واریز شد"
                response.data["status_text"] = "عمیات موفق"
                TransactionApiLogger.info(
                    f"transaction successfully done for user {order.user.oid}, order: {order.id}")
                PaymentApiLogger.info(
                    f"payment completed for user {order.user.id}, order_id: {order.id}, message: {response.data['status_code_msg']}")

        else:
            order.status = Order.OrderStats.CANCELLED
            response.data[
                "message"] = f"متاسفانه پرداخت شما موفقیت آمیز نبود\nلطفا مجدد تلاش کنید\nدر صورت کسر وجه، تا 72 ساعت آینده به حساب شما بازمیگردد\nدر غیر این صورت با پشتیبانی تماس بگیرید"
            response.data["status_text"] = "عمیات ناموفق"

            PaymentApiLogger.warning(
                f"payment failed for user {order.user.id}, order_id: {order.id} ,err: {response.data['status_code_msg']}")

            order.save()
        response.data["greet"] = f"{order.user.username} عزیز"
        res = render(request, 'zarinpal/verify-payment.html', context={"data": response.data})

        return res
