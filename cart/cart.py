# 데이터베이스에 저장하는 방식으로 만들지만 세션 기능을 활용해 만들어보자
# 세션으로 사용하는 방식이기 때문에 request.session에 데이터를 저장하고 꺼내오는 방식
# 이 때 세션에 값을 저장하려면 키 값을 설정해야 하는데 settings 에 CART_ID라는 변수를 만들고
# 거기에 설정된 값을 가져다가 사용하겠습니다.
from decimal import Decimal
from django.conf import settings
from shop.models import Product

class Cart(object):
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CARD_ID)
        if not cart: # 세션에 없던 키 값을 생성하면 자동저장
            cart = self.session[settings.CART_ID] = {}
            # 세션에 이미 있는 키 값에 대한 값을 수정하면 수동으로 저장
        self.cart = cart

    def __len__(self):
        # 요소가 몇개인지 갯수를 반환해주는 함수
            return sum(item['quantity'] for item in self.cart.values())

    def __iter__(self):
        # for문 같은 문법을 사용할 때 안에 있는 요소를 어떤 형태로 반환할 것인지 결정하는 함수
        product_ids = self.cart.keys()

        products = Product.objects.filter(id__in=product_ids) # __in 주어진 리스트 안에 존재하는 자료 탐색 ex) id가 product_ids인 자료 검색

        for product in products:
                self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
                item['price'] = Decimal(item['price'])
                item['total_price'] = item['price'] * item['quantity'] # 수량*가격

                yield item

    def add(self,product,quantity=1, is_update=False):
        product_id = str(product.id)
        if product_id not in self.cart: # 제품번호가 cart에 없으면
            # 만약 제품 정보가 Decimal 이라면 세션에 저장할 대는 str로 형변환해서 저장하고
            # 꺼내올 때는 Decimal로 형변환해서 사용해야 한다.
            self.cart[product_id] = {'quantity':0, 'price':str(product.price)} # 수량을 0으로 가격은 제품 가격을
            #
        if is_update: # is_update 가 true면
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        self.save()

    def save(self): # 장바구니에 상품을 담고
        self.session[settings.CART_ID] = self.cart
        self.session.modified = True

    def remove(self,product): # 장바구니의 상품을 삭제
        product_id = str(product.id)
        if product_id in self.cart:
            del(self.cart[product_id])
            self.save()

    def clear(self): # 장바구니를 비우는 기능, 주문 완료했을 때도 사용
        self.session[settings.CART_ID] = {}
        self.session.modified = True

    def get_product_total(self): # 장바구니에 담긴 상품의 총 가격을 계산
        return sum(Decimal(item['price'])*item['quantity'] for item in self.cart.values())