from pandas import DataFrame

from rest_framework import serializers, viewsets
from .model import Stock


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['user', 'symbol', 'price', 'created_at']

class SimpleStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['stock_code']

class PandasSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        return DataFrame(data)

    def to_representation(self, instance):
        return instance.to_dict()
