
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .model import *
from .utils import get_k_history,get_ma_frame,get_macd_frame
import logging
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
        return Response({'error': '缺少code参数'})

@api_view(['POST'])
def query_my_stock(request):
    userId = request.data.get('userId')
    userstockinfo = UserStocks.objects.filter(userId=userId)
    return Response(userstockinfo.to_dict())

@api_view(['POST'])
def find_stock(request):
    stock_id = request.data.get('stockId')


@api_view(['POST'])
def modified_stock(request):
    userId = request.data.get('userId')
    stock_id = request.data.get('stockId')
    action = request.data.get('action')
    type = request.data.get('type')
    UserStocks.updateStock(userId,stock_id,action,type)
    return Response({"success":"true"})

@api_view(['POST'])
def init_stock(request):
    # 登陆系统
    lg = bs.login()
    # 显示登陆返回信息

    # 获取沪深300成分股
    rs = bs.query_hs300_stocks()
    zs = bs.query_sz50_stocks()
    zz = bs.query_zz500_stocks()

    # 打印结果集
    #while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起



    # 登出系统
    bs.logout()
