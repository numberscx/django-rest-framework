from operator import truediv
from time import sleep
from urllib.parse import urlencode
import pandas as pd
import requests
import time
import pandas_ta as ta
import numpy as np
from .model import *
import logging
from .basicTa import macdScx
logger = logging.getLogger("util")


def gen_eastmoney_code(rawcode: str) -> str:
    '''
    生成东方财富专用的secid
    Parameters
    ----------
    rawcode ： 6 位股票代码
    Parameters
    ----------
    str : 按东方财富格式生成的字符串
    '''
    if rawcode[0] != '6':
        return f'0.{rawcode}'
    else:
        return f'1.{rawcode}'

def get_k_history(code: str, beg: str = '20230101', end = '10000204', klt: int = 101,
                  fqt: int = 1) -> pd.DataFrame:
    '''
    功能获取k线数据
    Parameters
    ----------
    code : 6 位股票代码
    beg: 开始日期 例如 20200101
    end: 结束日期 例如 20200201
    klt: k线间距 默认为 101 即日k
        klt:1 1 分钟
        klt:5 5 分钟
        klt:101 日
        klt:102 周
    fqt: 复权方式
        不复权 : 0
        前复权 : 1
            后复权 : 2
    Return
    ------
    DateFrame : 包含股票k线数据
    '''
    if(end == '10000204'):
        current_time = time.time()
        end = time.strftime("%Y%m%d", time.localtime(current_time))
    EastmoneyKlines = {
        'f51': '时间',
        'f52': '开盘',
        'f53': '收盘',
        'f54': '最高',
        'f55': '最低',
        'f56': '成交量',
        'f57': '成交额',
        'f58': '振幅',
        'f59': '涨跌幅',
        'f60': '涨跌额',
        'f61': '换手率',
    }
    EastmoneyHeaders = {

        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Referer': 'http://quote.eastmoney.com/center/gridlist.html',
    }
    fields = list(EastmoneyKlines.keys())
    columns = list(EastmoneyKlines.values())
    fields2 = ",".join(fields)
    secid = gen_eastmoney_code(code)
    params = (
        ('fields1', 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13'),
        ('fields2', fields2),
        ('beg', beg),
        ('end', end),
        ('rtntype', '6'),
        ('secid', secid),
        ('klt', f'{klt}'),
        ('fqt', f'{fqt}'),
    )
    base_url = 'https://push2his.eastmoney.com/api/qt/stock/kline/get'
    url = base_url + '?' + urlencode(params)
    json_response = requests.get(
        url, headers=EastmoneyHeaders).json()
    data = json_response['data']
    # code = data['code']
    # 股票名称
    # name = data['name']
    if not data:
        return pd.DataFrame()
    klines = data['klines']
    rows = []
    for _kline in klines:
        kline = _kline.split(',')
        rows.append(kline)
    df = pd.DataFrame(rows, columns=columns)
    df['收盘'] = df['收盘'].astype(float)
    df['开盘'] = df['开盘'].astype(float)

    return df

def get_ma_frame(kdataFrame : pd.DataFrame):
    kdata = kdataFrame['收盘']
    print(kdata.size)
    ma_5 = ta.sma(kdata, 5)
    ma_10 = ta.sma(kdata, 10)
    ma_20 = ta.sma(kdata, 20)
    ma_60 = ta.sma(kdata, 60)

    ma_5 = ma_5.replace(np.NaN, 0)
    ma_10 = ma_10.replace(np.NaN, 0)
    ma_20 = ma_20.replace(np.NaN, 0)
    ma_60 = ma_60.replace(np.NaN, 0)

    rows = []
    for i in range(0, ma_5.size):
        rows.append([ma_5[i], ma_10[i], ma_20[i], ma_60[i]])

    ma_frame = pd.DataFrame(rows,columns=['ma5','ma10','ma20','ma60'])
    ma_frame.fillna(0, inplace=True)
    return pd.concat([kdataFrame, ma_frame], axis=1)


def get_macd_frame(kdataFrame: pd.DataFrame):
    kdata = kdataFrame['收盘']
    fastma,slowma,macd = macdScx(kdata)
    macd = macd.replace(np.NaN, 0)
    slowma = slowma.replace(np.NaN, 0)
    fastma = fastma.replace(np.NaN, 0)

    macd.fillna(0, inplace=True)
    slowma.fillna(0, inplace=True)
    fastma.fillna(0, inplace=True)

    rows = []
    for i in range(0, len(slowma)):
        rows.append([slowma[i], fastma[i],macd[i]])
    df = pd.DataFrame(rows, columns=['macds', 'macdf', 'macd'])

    return pd.concat([kdataFrame, df], axis=1)

def get_single_json_response(data):
    return data.serialize()


def get_list_json_response(data):
    context = super().get_serializer_context()
    context['data'] = [item.serialize() for item in data]
    return context


def compute_buy_and_sell(kdataFrame: pd.DataFrame):
    close = kdataFrame['收盘']
    open = kdataFrame['开盘']
    ma5 = kdataFrame['ma5']
    ma10 = kdataFrame['ma10']

    markPoint = np.zeros((close.size,))

    for i in range(close.size):
        if (i > 22):
            # 若前五天的开盘、收盘均低于ma5，且当天上穿ma5，则标记为买点
            if (judge_buy(close, open, ma5, ma10, i)):
                markPoint[i] = 1
            elif (judge_sell(close, open, ma5, ma10, i, markPoint)):
                markPoint[i] = -1
    rows = []
    for i in range(0, markPoint.size):
        rows.append([markPoint[i]])
    mark_point_frame = pd.DataFrame(rows, columns=['buyAndSell'])
    return pd.concat([kdataFrame, mark_point_frame], axis=1)

def compute_buy_and_sell_real(kdataFrame: pd.DataFrame,userId,stockCode):
    close = kdataFrame['收盘']
    open = kdataFrame['开盘']
    ma5 = kdataFrame['ma5']
    ma10 = kdataFrame['ma10']

    userStock = UserStocks.objects.filter(user_id=userId).first()
    print("find userstock",userStock)
    userHolding = userStock.holding_stocks.split(",")
    print("userHolding",userHolding)
    for i in range(close.size):
        if (i > 22):
            # 若前五天的开盘、收盘均低于ma5，且当天上穿ma5，则标记为买点
            if (judge_buy_real(close, open, ma5, ma10)):
                return 1
            elif (stockCode in userHolding and judge_sell_real(close, open, ma5, ma10)):
                return -1

def judge_buy_real(close, open, ma5, ma10):
    # 连续5天的开盘或者收盘均低于10日均线，再涨15%就突破十日均线
    if (ma10[-1] > max(close[-5:]) and ma10[-1] > max(open[-5:]) and close[-1]>open[-1] and (ma10[-1]-close[-1])/close[-1] <0.1):
        return True
    return False


def judge_sell_real(close, open, ma5, ma10):
    if(close[-1]<ma5):
        return True
    return False


# 若前3天的收盘均低于ma10，且当天上穿ma10，并且已经涨了两天了
def judge_buy(close, open, ma5, ma10, i):
    if(ma10[i-1]>max(close[i-3:i]) and close[i]>ma10[i] and close[i-2]>=open[i-2] and close[i-1]>=open[i-1]):
        return True
    return False

# 若前3天收盘均高于ma5，且当天下穿ma5，且上一个点为买点
def judge_sell(close, open, ma5, ma10, i, markPoint):
    if(ma5[i]<min(close[i-3:i]) and close[i] < open[i] and close[i]<ma5[i]):
        hasBuy = False
        for j in range(1,i):
            if(markPoint[i-j] == -1):
                break;
            elif(markPoint[i-j] == 1):
                hasBuy = True
                break
        return hasBuy
    return False
from django.apps import apps

# 每日根据收盘计算macd处于跌势末尾，jdk快线上穿慢线
def computeDailyStock():
    # 定时任务，需要懒加载模型
    initStock = apps.get_model('example', 'Stock')  # 获取延迟加载的模型

    allstock = initStock.objects.all()
    return_result = ""
    length = len(allstock)
    thisSeri = 0
    for stock in allstock:
        thisSeri = thisSeri + 1
        stockcode = stock.__str__()
        logger.debug("computeDailyStock stock_code = "+stockcode)
        kdataFrame = get_k_history(stockcode)
        if kdataFrame.empty:
            print("cant find stock data" + stockcode)
            logger.debug("cant find stock data" + stockcode)
            continue
        smaDataFrame = get_ma_frame(kdataFrame)
        macdDataFrame = get_macd_frame(smaDataFrame)

        # kArray = macdDataFrame['收盘']
        # k,d,j = calculate_kdj(kArray)
        msg,needAdd = macdStrategy(macdDataFrame)
        expandMsg = '股票代码 '+stockcode + '\n交易建议 ' +msg +'\n \n'
        if(needAdd):
            return_result = return_result + expandMsg
        sleep(1)
        print(expandMsg + ' ' + str(thisSeri) + '/' + str(length))
        logger.debug(expandMsg)
    return return_result


# macd策略，macd小于0，且快线从下方与顶点分离，且快线后续上穿慢线，则为多方信号
# macd大于0，且快线从上方与顶点分离，且快线后续上穿慢线，则为空方信号
def macdStrategy(macdDataFrame: pd.DataFrame):
    macdslow = macdDataFrame['macds']
    macdfast = macdDataFrame['macdf']
    macd = macdDataFrame['macd']
    maxlen = len(macd)

    if(macd[maxlen-5]*macd[maxlen-4]<=0 or macd[maxlen-4]*macd[maxlen-3]<=0 or macd[maxlen-3]*macd[maxlen-2]<=0 or macd[maxlen-2]*macd[maxlen-1]<=0):
        if(macd[maxlen-1]>0):
        # 判断是否快线上穿了慢线(五天内差值相乘小于等于0)，多方信号
            maxOne,maxSeri = findSpecialPoint(macd,-1)
            if(macdfast[maxSeri]<maxOne):
                return "涨价区间",True
        else:
            maxOne,maxSeri = findSpecialPoint(macd,1)
            if(macdfast[maxSeri]>maxOne):
                return "降价区间",True

    return "ignore",False

def findSpecialPoint(macd, symbol):
    maxOne = 0
    maxSeri = -1
    begseri = len(macd)-1
    while(macd[begseri]*symbol<=0):
        begseri-=1
    endseri = begseri
    while(macd[endseri]*symbol>0):
        endseri-=1
    for i in range(endseri,begseri+1):
        if(macd[i]*symbol>maxOne):
            maxOne = macd[i]*symbol
            maxSeri = i
    return maxOne*symbol,maxSeri

def calculate_kdj(data):
    n = len(data)
    k_values, d_values, j_values = [], [], []

    for i in range(n):
        if i < 8:
            k_values.append(0)
            d_values.append(0)
            j_values.append(0)
            continue

        lowest_low = min(data[i - 8: i + 1])
        highest_high = max(data[i - 8: i + 1])

        rsv = (data[i] - lowest_low) / (highest_high - lowest_low) * 100

        if i == 8:
            k = rsv
            d = rsv
        else:
            k = (2 / 3) * k_values[i - 8] + (1 / 3) * rsv
            d = (2 / 3) * d_values[i - 8] + (1 / 3) * k

        j = 3 * k - 2 * d
        k_values.append(k)
        d_values.append(d)
        j_values.append(j)

    return k_values, d_values, j_values

def send_wechat(msg):
    token = 'de25e20f7de54968b6edd2243ec1441a'#前边复制到那个token
    current_time = time.time()

    end = time.strftime("%Y%m%d", time.localtime(current_time))

    title = end+'股票量化分析'
    content = msg
    template = 'markdown'
    url = f"https://www.pushplus.plus/send?token={token}&title={title}&content={content}&template={template}"
    print(url)
    r = requests.get(url=url)
    print(r.text)

