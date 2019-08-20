from django.urls import path
from .views import *

app_name = 'orders'

urlpatterns = [
    path('create/', order_create, name='order_create'), # create form 을 호출
    path('create_ajax/', OrderCreateAjaxView.as_view(), name='order_create_ajax'),
    path('checkout/', OrderCheckoutAjaxView.as_view(), name='order_checkout'),
    path('validation/', OrderImpAjaxView.as_view(),name='order_validation'), # 결제 후 검증
    path('complete/', order_complete, name='order_complete'), # 주문 완료 화면
]