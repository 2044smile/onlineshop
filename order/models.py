from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator # validators 값의 범위를 지정해주는

from coupon.models import Coupon
from shop.models import Product
from .iamport import payments_prepare, find_transcation
import hashlib


class Order(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    coupon = models.ForeignKey(Coupon, on_delete=models.PROTECT, related_name='order_coupon', null=True, blank=True)
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0),MaxValueValidator(100000)])
    # validators 값의 범위를 지정해주는

    class Meta:
        ordering = ['-created']

    def __str__(self):
            return 'Order {}'.format(self.id)

    def get_total_product(self):
            return sum(item.get_item_price() for item in self.items.all())

    def get_total_price(self):
            total_product = self.get_total_product()
            return total_product - self.discount


class OrderItem(models.Model):# 해당 모델은 주문에 포함된 제품 정보를 담기 위해 만드는 모델입니다.
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    # 고정 소수로 python 에서 Decimal 인스턴스로 나타낸다. / max_Digits 숫자에 허용되는 최대 자릿수다.
    # 이 숫자는 decimal_places보다 크거나 같아야 한다. decimal_places 숫자와 함께 저장될 소수 자릿수다.
    # 예를 들어 최대 999를 소수점 2자리 이하로 저장하기 위해서 다음과 같이 사용
    # models.DecimalField(..., max_digits=5, decimal_places=2) 소수점 포함 5자리이므로 999.99 !!
    def __str__(self):
        return '{}'.format(self.id)

    def get_item_price(self):
        return self.price * self.quantity


class OrdertransactionManager(models.Manager): # 모델 매니저는 데이터베이스 쿼리와 연동되는 인터페이스다
    # OrderTransaction 모델의 매니저 클래스이다. 우리가 지금까지 사용했던 모델의 경우 기본 모델은 objects이다.
    # 이 objects 대신에 다른 메서드들을 만들어 사용하기 위해 매니저 클래스를 만들었습니다.
    # 이 매니저는 결제 정보를 생성할 때 해시 함수를 사용해 merchant_order_id를 만들어 냅니다. 이는
    # 아임포트 쪽으로 결제 요청을 할 때 유니크한 주문번호가 필요하기 때문이다. 그리고 결제 이후에 제대로된 결제정보를 검색하는데 도움된다.
    def create_new(self,order,amount,success=None,transaction_status=None):
        if not order:
            raise ValueError("주문 오류")
    #
        order_hash = hashlib.sha1(str(order.id).encode('utf-8')).hexdigest()
        email_hash = str(order.email).split("@")[0]
        final_hash = hashlib.sha1((order_hash + email_hash).encode('utf-8')).hexdigest()[:10]
        merchant_order_id = "%s"%(final_hash)
        payments_prepare(merchant_order_id,amount)

        transaction = self.model(
            order=order,
            merchant_order_id=merchant_order_id,
            amount=amount
        )

        if success is not None:
            transaction.success = success
            transaction.transaction_status = transaction_status

        try:
            transaction.save()
        except Exception as e:
            print("save error",e)

        return transaction.merchant_order_id


    def get_transaction(self,merchant_order_id):
        result = find_transcation(merchant_order_id)
        if result['status'] == 'paid':
            return result
        else:
            return None


class OrderTransaction(models.Model): # 결제 정보를 저장할 때 사용한다
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    merchant_order_id = models.CharField(max_length=120, null=True, blank=True)
    transaction_id = models.CharField(max_length=120, null=True, blank=True) # 매우 중요한 정보 정산문제확인과 환불할 때 필요한 정보
    amount = models.PositiveIntegerField(default=0)
    transaction_status = models.CharField(max_length=220, null=True, blank=True)
    type = models.CharField(max_length=120,blank=True)
    created = models.DateTimeField(auto_now=False)

    objects = OrdertransactionManager()

    def __str__(self):
        return str(self.order.id)

    class Meta:
        ordering = ['-created']


def order_payment_validation(sender, instance, created, *args, **kwargs):
    if instance.transaction_id:
        import_transaction = OrderTransaction.objects.get_transaction(merchant_order_id=instance.merchant_order_id)
        merchant_order_id = import_transaction['merchant_order_id']
        imp_id = import_transaction['imp_id']
        amount = import_transaction['amount']

        local_transaction = OrderTransaction.objects.filter(merchant_order_id=merchant_order_id, transaction_id = imp_id, amount=amount).exists()
        if not import_transaction or not local_transaction:
            raise ValueError("비정상 거래입니다.")



from django.db.models.signals import post_save # 결제 정보가 생성된 후에 호출함 함수를 연결해준다.
post_save.connect(order_payment_validation,sender=OrderTransaction)
# 시그널을 활용한 결제 검증 함수이다. 시그널이란 특정 기능이 수행되었음을 장고 애플리케이션 전체에 알리는 용도입니다.
# 이 시그널을 이용해 특정 기능 수행 전 혹은 수행 후에 별도의 로직을 추가할 수 있습니다. 이번 경우에는 OrderTransaction 모델의 객체가
# 추가되면 그 후에 결제 검증을 하는 함수를 호출하도록 연결했습니다.
