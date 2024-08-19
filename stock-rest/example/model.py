
from django.db import models

class Stock(models.Model):
    user = models.CharField(max_length=10)
    symbol = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    stock_code = models.CharField(max_length=10)

    def __str__(self):
        return self.symbol


class StockKInfo(models.Model):
    k_value = models.FloatField()
    close_date = models.DateTimeField()

    ma_5 = models.FloatField()
    ma_10 = models.FloatField()
    ma_20 = models.FloatField()


    def __str__(self):
        return self.k_value





