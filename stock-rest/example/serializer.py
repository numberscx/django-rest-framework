from pandas import DataFrame
from .model import *
from rest_framework import serializers


class PandasSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        return DataFrame(data)

    def to_representation(self, instance):
        return instance.to_dict()

class UserStockSerializer(serializers.Serializer):
    # holding_stocks
    # attention_stocks
    # userId
    class Meta:
        model = UserStocks
        fields = ['attention_stocks', 'holding_stocks']

class StockSerializer(serializers.Serializer):
    # holding_stocks
    # attention_stocks
    # userId
    def to_representation(self,stock):
        return {
            'stock_name': stock.stock_name,
            'stock_code': stock.stock_code
        }

class MySerializer(serializers.Serializer):
    def serialize(self, instance, format=None, fields=None, many=False):
        print(instance)
        data = super().serialize(instance, format, fields, many)
        data['my_field'] = 'my_value'
        return data