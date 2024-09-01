from operator import truediv
from urllib.parse import urlencode
import pandas as pd
import requests
import time
import pandas_ta as ta
import numpy as np


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

def get_k_history(code: str, beg: str = '20200101', end = '10000204', klt: int = 101,
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
    print(ma_frame)
    ma_frame.fillna(0, inplace=True)
    return pd.concat([kdataFrame, ma_frame], axis=1)


def get_macd_frame(kdataFrame: pd.DataFrame):
    kdata = kdataFrame['收盘']
    macd = ta.macd(kdata)
    macd = macd.replace(np.NaN, 0)


    macd.fillna(0, inplace=True)
    return pd.concat([kdataFrame, macd], axis=1)

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
            elif (judge_sell(close, open, ma5, ma10, i)):
                markPoint[i] = -1
    rows = []
    for i in range(0, markPoint.size):
        rows.append([markPoint[i]])
    mark_point_frame = pd.DataFrame(rows, columns=['buyAndSell'])
    return pd.concat([kdataFrame, mark_point_frame], axis=1)


# 若前3天的收盘均低于ma5，且当天上穿ma5，则标记为买点
def judge_buy(close, open, ma5, ma10, i):
    if(ma5[i]>max(close[i-3:i]) and close[i] > open[i] and close[i]>ma5[i]):
        return True
    return False

# 若前3天收盘均高于ma5，且当天下穿ma5，则标记为卖点
def judge_sell(close, open, ma5, ma10, i):
    if(ma5[i]<min(close[i-3:i]) and close[i] < open[i] and close[i]<ma5[i]):
        return True
    return False