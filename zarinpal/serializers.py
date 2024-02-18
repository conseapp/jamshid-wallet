from rest_framework import serializers


class PaymentRequestSerializer(serializers.Serializer):
    Amount = serializers.IntegerField()
    Description = serializers.CharField(max_length=200)
    Phone = serializers.CharField(max_length=11)
