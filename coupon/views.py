from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import redirect
from django.views.decorators.http import require_POST # 뷰가 POST인 메소드만 허용하는 데코레이터
from .models import Coupon
from .forms import AddCouponForm

@require_POST
def add_coupon(request):
    now = timezone.now() # 현재 시간을 now에 저장
    form = AddCouponForm(request.POST) # AddCouponForm 에 입력 후 post로 전송한 값들을 form 에 저장
    # 입력한 쿠폰코드를 이용해 쿠폰을 조회한다
    if form.is_valid():
        code = form.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(code__iexact=code, use_from__lte=now,
                                        use_to__gte=now, active=True)
            #*iexact 대소문자 구분없이 일치하는 코드 찾기, get 메서드나 filter를 사용해 원하는 데이터를 찾을 때는
            # 각 필드명__옵션 형태로 질의를 만들 수 있다.ex)code__iexact
            # use_form이 현재 시간보다 이전이어야 하고 use_to는 현재 시간보다 이후여야 하므로 __lte, __gte옵션을 걸었다.
            request.session['coupon_id'] = coupon.id # 이런 옵션으로 검색한 조건이 존재하면 쿠폰의 did 값을 세션에 저장하고
        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None
        return redirect('cart:detail') # 장바구니로 돌아간다.
