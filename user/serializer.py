from rest_framework import serializers


class GeneratePayLinkSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    amount = serializers.IntegerField()


class URLSerializer(serializers.Serializer):
    order_id = serializers.CharField(required=True)
    return_url = serializers.URLField(required=False, allow_null=True)
