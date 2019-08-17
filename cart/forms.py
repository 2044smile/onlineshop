from django import forms

class AddProductForm(forms.Form):
    # 상품 수량 설정 field
    quantity = forms.IntegerField()
    # 수정 여부 확인 field
    is_update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)

# is_update는 상세 페이지에서 추가할 때와 장바구니에서 수량을 바꿀 때 동작하는 방식을
# 달리하려고 사용하는 변수입니다.제품 상세 페이지에서는 제품 수량을 선택하고 추가할 때
# 마다 현재 장바구니 수량에 더해주는 방식을 취할 것이기 때문에 is_update의 값은 False여야 한다.
# 반면에 장바구니 페이지에서 수량을 변경하는 것은 그 값을 그대로 현재 수량에 반영해야 하기 때문에
# is_update는 True로 설정할 것 입니다.