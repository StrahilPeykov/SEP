from rest_framework import serializers
from core.models import Product

class ProductSerializer(serializers.ModelSerializer):
    supplier = serializers.PrimaryKeyRelatedField(read_only=True)
    emission_total = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"

    def get_emission_total(self, obj: Product) -> float:
        return obj.get_emission_trace().total