from yaml import serialize

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .model import *
from .innerModel import *
from .utils import *
import logging
from .serializer import *
import baostock as bs
import time
from datetime import datetime
import os


logger = logging.getLogger(__name__)


@api_view(['POST'])
def query_simple_stock(request):
    code = request.data.get('code')
    if(code):
        kdataFrame,name = get_k_history(code)
        if kdataFrame.empty:
            return Response(HttpFailure().to_representation())
        smaDataFrame = get_ma_frame(kdataFrame)
        macdDataFrame = get_macd_frame(smaDataFrame)
        # todo remove
        print(macdDataFrame)
        computeBuySellDataFrame = compute_buy_and_sell(macdDataFrame)
        return Response(computeBuySellDataFrame.to_dict())
    else:
        return Response(HttpFailure().to_representation())

@api_view(['POST'])
def query_my_stock(request):
    userId = request.data.get('userId')
    userstockinfo = UserStocks.objects.filter(userId=userId)
    serializers = StockSerializer(userstockinfo, many=True)
    return Response(serializers.data)

@api_view(['POST'])
def find_stock(request):
    allstock = Stock.objects.all()
    print("allstock:")
    serializers = StockSerializer(allstock, many=True)
    return Response(serializers.data)

@api_view(['POST'])
def findCommandStock(request):
    date = request.data.get('date')
    print(date)
    file_path = date + '.xlsx'

    if not os.path.exists(file_path):
        return Response(HttpFailure().to_representation())
    # 使用pandas读取xlsx文件
    df = pd.read_excel(file_path)

    return Response(df.to_dict())


@api_view(['POST'])
def modified_stock(request):
    userId = request.data.get('userId')
    stock_id = request.data.get('stockId')
    action = request.data.get('action')
    type = request.data.get('type')

    newlist = UserStocks.updateStock(userId,stock_id,action,type)
    httpsu = HttpSuccess()
    httpsu.msg = newlist
    return Response(httpsu.to_representation())

@api_view(['GET'])
def queryDailyStock(request):
    msg= computeDailyStock()
    send_wechat(msg)
    logger.debug("dailyStockCompute " + msg)
    return Response({'success': True,
            'msg': msg})


@api_view(['POST'])
def query_chance(request):
    userId = request.data.get('userId')
    if userId!="scx":
        return Response(HttpFailure().to_representation())
    allstock = Stock.objects.all()

    now = datetime.now()
    now_str = now.strftime("%Y%m%d")

    six_months_ago = now - datetime.timedelta(days=180)
    start_str = six_months_ago.strftime("%Y%m%d")
    f = open(now_str+"_"+userId+".txt", 'a') # 读取label.txt文件，没有则创建，‘a’表示再次写入时不覆盖之前的内容

    for stock in allstock:
        kdataFrame,name = get_k_history(stock.stock_code, beg=start_str, end=now_str)
        if kdataFrame.empty:
            continue
        smaDataFrame = get_ma_frame(kdataFrame)
        buyOrSell = compute_buy_and_sell_real(smaDataFrame, userId,stock.stock_code)
        if buyOrSell == 1:
            f.write("time to buy "+stock.stock_code)
            f.write('\n')
            f.close()
        elif buyOrSell == -1:
            f.write("time to sell " + stock.stock_code)
            f.write('\n')
            f.close()
        time.sleep(1)



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
    return Response(HttpSuccess().to_representation())

