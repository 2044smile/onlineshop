from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Coupon(models.Model):
    code = models.CharField(max_length=50,unique=True)
    use_from = models.DateTimeField() # 쿠폰의 사용기간 지정
    use_to = models.DateTimeField() # 쿠폰의 사용기간 지정
    amount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100000)]) # 할인 금액
    active = models.BooleanField()

    def __str__(self):
        return self.code