from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
# 뷰가 POST인 메소드만 허용하는 데코레이터

from  shop.models import Product
from .forms import AddProductForm
from .cart import Cart # cart.py

# 제품 정보를 전달 받으면 카트 객체에 제품 객체를 추가합니다.
# 이 때 추가하는 제품의 정보는 상세 페이지 혹은 장바구니 페이지로부터 전달되며
# AddProductForm을 통해 만들어진 데이터 입니다.
@require_POST
def add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    form = AddProductForm(request.POST) # AddProductForm 에서 입력 된 form 들을 form에 저장
    if form.is_valid(): # 문제없는 form 인지 유효성 검삭
        cd = form.cleaned_data # 유효성 검사가 끝난 데이터들을 cd에 넣고
        cart.add(product=product, quantity=cd['quantity'], is_update=cd['is_update']) # 값을 추가

        return redirect('cart:detail')

