
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import StockSerializer
from .utils import get_k_history,get_ma_frame,get_macd_frame

@api_view(['GET'])
def get_stock_view(reuqest):
    return Response(StockSerializer({"user":"acx","symbol":"as","price":123,"created_at":"2024-08-18 00:00:00"}).data);

@api_view(['POST'])
def query_simple_stock(request):
    print(request)
    code = request.data.get('code')
    print(code)
    if(code):
        kdataFrame = get_k_history(code)
        smaDataFrame = get_ma_frame(kdataFrame)
        macdDataFrame = get_macd_frame(smaDataFrame)
        return Response(macdDataFrame.to_dict())
    else:
        return Response({'error': '缺少code参数'})

