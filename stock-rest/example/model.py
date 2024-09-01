from django.db import models

# Create your models here.
class User(models.Model):
    user_id = models.CharField(max_length=32, primary_key=True)
    nick_name = models.CharField(max_length=32)
    register_platform = models.CharField(max_length=32)
    create_time = models.DateTimeField()
    modified_time = models.DateTimeField()
    credit_level = models.CharField(max_length=32)
    extra_info = models.CharField(max_length=256)
    operation_info = models.CharField(max_length=1024)

    def __json__(self):
        return {
            'user': self.name,
            'age': self.age
        }

    def __str__(self):
        return self.user_id

class Stock(models.Model):
    stock_code = models.CharField(max_length=10, primary_key=True)
    stock_name = models.CharField(max_length=32)

    career_id = models.CharField(max_length=10)
    attention_user_ids = models.TextField()
    holding_user_ids = models.TextField()
    quality = models.CharField(max_length=3)

    # def serialize(self):
    #     return self.data

    def __str__(self):
        return self.stock_code

    def save(self):
        temp_user_id = self.stock_code
        order_exists = Stock.objects.filter(stock_code=temp_user_id)
        if order_exists.exists():
            print('股票已经存在，现在更新数据')
            '''此处注意，这里默认更新的是最后一条数据'''
            self.stock_code = order_exists.last().stock_code
        else:
            pass
        super().save()



class UserStocks(models.Model):
    user_id = models.CharField(max_length=32, primary_key=True)
    attention_stocks = models.TextField()
    holding_stocks = models.TextField()
    #
    # def serialize(self):
    #     return self.data

    def __str__(self):
        return self.user_id

    def updateStock(self, userId,stock_id, action, type):
        userstock = UserStocks.objects.filter(user_id=userId)
        if action == "attention":
            stockText = userstock.get("attention_stocks");
        else:
            stockText = userstock.get("holding_stocks");
        stockList = stockText.split(",")
        if type == "remove":
            stockList.remove(stock_id)
        else:
            stockList.append(stock_id)
        newStockText = ",".join(stockList)
        if action == "attention":
            UserStocks.objects.filter(user_id=userId).update(attention_stocks=newStockText)
        else:
            UserStocks.objects.filter(user_id=userId).update(holding_stocks=newStockText)

class StockDatas(models.Model):
    stock_code = models.CharField(max_length=10, unique=True)
    stock_name = models.CharField(max_length=32)
    history_k_info = models.TextField()
    basic_info = models.TextField()
    gmt_modified = models.DateTimeField()

    # def serialize(self):
    #     return self.data
    def __str__(self):
        return self.stock_code


