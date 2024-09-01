from yaml import serialize

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .model import *
from .innerModel import *
from .utils import *
import logging
from .serializer import *
import pandas as pd
import baostock as bs


logger = logging.getLogger(__name__)


@api_view(['POST'])
def query_simple_stock(request):
    code = request.data.get('code')
    if(code):
        kdataFrame = get_k_history(code)
        smaDataFrame = get_ma_frame(kdataFrame)
        macdDataFrame = get_macd_frame(smaDataFrame)
        return Response(macdDataFrame.to_dict())
    else:
        return Response(MySerializer.serialize(HttpFailure()))

@api_view(['POST'])
def query_my_stock(request):
    userId = request.data.get('userId')
    userstockinfo = UserStocks.objects.filter(userId=userId)

    return Response(MySerializer.serialize(userstockinfo))

@api_view(['POST'])
def find_stock(request):
    allstock = Stock.objects.all()
    print("allstock:")
    print(allstock)
    serialize = MySerializer(allstock, many=True)
    return Response(serialize.data)

@api_view(['POST'])
def modified_stock(request):
    userId = request.data.get('userId')
    stock_id = request.data.get('stockId')
    action = request.data.get('action')
    type = request.data.get('type')
    UserStocks.updateStock(userId,stock_id,action,type)

    return Response(MySerializer.serialize(HttpSuccess()))

@api_view(['POST'])
def init_stock(request):
    # 登陆系统
    lg = bs.login()
    # 显示登陆返回信息

    # 获取沪深300成分股
    rs = bs.query_hs300_stocks()
    zs = bs.query_sz50_stocks()
    zz = bs.query_zz500_stocks()
    # 登出系统
    bs.logout()
    # 打印结果集
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        stock = Stock()
        stock.stock_code = (rs.get_row_data()[1]).split('.')[1]
        stock.stock_name = rs.get_row_data()[2]
        stock.save()
    while (zs.error_code == '0') & zs.next():
        # 获取一条记录，将记录合并在一起
        stock = Stock()
        stock.stock_code = (zs.get_row_data()[1]).split('.')[1]
        stock.stock_name = zs.get_row_data()[2]
        stock.save()
    while (zz.error_code == '0') & zz.next():
        # 获取一条记录，将记录合并在一起
        stock = Stock()
        stock.stock_code = (zz.get_row_data()[1]).split('.')[1]
        stock.stock_name = zz.get_row_data()[2]
        stock.save()
    return Response(MySerializer.serialize(HttpSuccess()))

