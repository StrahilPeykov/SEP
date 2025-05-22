from rest_framework import serializers


class NullListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        iterable = super().to_representation(data)
        return [None for _ in iterable]

class NullSerializer(serializers.Serializer):
    """
    A serializer that always serializes any single object to null.
    """
    list_serializer_class = NullListSerializer

    def to_representation(self, instance):
        return None

    def to_internal_value(self, data):
        return None