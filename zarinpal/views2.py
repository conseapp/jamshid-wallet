import json

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from zarinpal.serializers import PaymentRequestSerializer
from zarinpal.utils import sent_payment_request


class PaymentRequestView(APIView):
    serializer_class = PaymentRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            response = sent_payment_request(serializer.data)
            if response.status_code == 200:
                print(response.data["authority"])
            return response
        else:
            return Response(data={"message": "invalid data"}, status=status.HTTP_400_BAD_REQUEST)


class PaymentVerifyView(APIView):

    def get(self, request):
        authority = request.query_params.get('Authority')
        status = request.query_params.get('Status')
        data = {"status": str(status), "authority": str(authority)}
        print(data)
        return Response(data=data)
