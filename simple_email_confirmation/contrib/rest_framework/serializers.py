from rest_framework import serializers

from simple_email_confirmation import get_email_address_model


class EmailAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_email_address_model()
        fields = (
            'pk',
            'email',
            'is_confirmed',
            'is_primary',
        )


class ConfirmEmailAddressSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    code = serializers.CharField()
