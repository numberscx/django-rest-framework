"""
URL configuration for example project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import query_simple_stock,query_my_stock,find_stock,modified_stock,init_stock

urlpatterns = [
    path('admin/', admin.site.urls),
    # 单股票的k线计算
    path('querysimple/', query_simple_stock, name='user-query-stocks'),
    # 查询我的股票列表
    path('querystocks/', query_my_stock, name='user-my-stocks'),
    # 查询一个股票，若数据库没有，则查询相关信息并建立股票资料
    path('findstock/', find_stock, name='find-stocks'),
    # 查询一个股票，若数据库没有，则查询相关信息并建立股票资料
    path('modifiedstock/', modified_stock, name='find-stocks'),
    path('initstock/', init_stock, name='init-stock'),
]
