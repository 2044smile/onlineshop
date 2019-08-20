from django import forms

from .models import Order


class OrderCreateForm(forms.ModelForm): # 주문서 작성 시 필요한 form 을 제작
    class Meta:
        model = Order
        fields = ['first_name','last_name','email','address','postal_code','city']