from rest_framework import serializers


class BulkActionSerializer(serializers.Serializer):
    """
    Serializer for bulk actions.
    """

    ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )