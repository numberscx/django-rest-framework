# import baostock as bs
# import pandas as pd
#
# # 登陆系统
# lg = bs.login()
# # 显示登陆返回信息
# print('login respond error_code:'+lg.error_code)
# print('login respond  error_msg:'+lg.error_msg)
#
# # 获取沪深300成分股
# rs = bs.query_hs300_stocks()
# print('query_hs300 error_code:'+rs.error_code)
# print('query_hs300  error_msg:'+rs.error_msg)
#
# # 打印结果集
# hs300_stocks = []
# while (rs.error_code == '0') & rs.next():
#     # 获取一条记录，将记录合并在一起
#     hs300_stocks.append(rs.get_row_data())
# result = pd.DataFrame(hs300_stocks, columns=rs.fields)
# # 结果集输出到csv文件
# result.to_csv("./hs300_stocks.csv", encoding="gbk", index=False)
# print(result)
#
# # 登出系统
# bs.logout()
# import requests
# #
#
#
# def send_wechat(msg):
#     token = 'de25e20f7de54968b6edd2243ec1441a'#前边复制到那个token
#     title = 'title1'
#     content = "股票代码交易建议\n\n"+msg
#     template = 'txt'
#     url = f"https://www.pushplus.plus/send?token={token}&title={title}&content={content}&template={template}"
#     print(url)
#     r = requests.get(url=url)
#     print(r.text)
#
# if __name__ == '__main__':
#     msg = 'Life is short I use python'
#     send_wechat(msg)

# import akshare as ak
#
# # 获取股票日线行情数据
# stock_data = ak.stock_zh_a_daily(symbol="sz000001", start_date="2022-01-01", end_date="2022-12-31")
# print(stock_data)
#
# fund_em_value_df = ak.fund_em_value(symbol="000001")
# print(fund_em_value_df.head())
from .schedule import __initSchedule__
__initSchedule__()
