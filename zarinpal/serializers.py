from rest_framework import serializers


class PaymentRequestSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    description = serializers.CharField(max_length=200)
    phone = serializers.CharField(max_length=11)
    type = serializers.ChoiceField(choices=[('deposit', 'DEPOSIT'), ('purchase', 'PURCHASE')])
    user_id = serializers.CharField(max_length=50)
    event_id = serializers.CharField(max_length=50, required=False)

    def validate(self, data):
        # Get the values of 'type' and 'event_id' from the validated data
        payment_type = data.get('type')
        event_id = data.get('event_id')

        # Check if the 'type' is 'purchase' and 'event_id' is not provided
        if payment_type == 'PURCHASE' and not event_id:
            raise serializers.ValidationError("event_id is required for 'purchase' type.")

        return data


class RegisterEventSerializer(serializers.Serializer):
    event_id = serializers.CharField(max_length=50, required=False)
    requested_at = serializers.IntegerField()

    def validate(self, data):
        # Get the values of 'type' and 'event_id' from the validated data
        event_id = data.get('event_id')
        requested_at = data.get('requested_at')

        # Check if the 'type' is 'purchase' and 'event_id' is not provided

        return data
