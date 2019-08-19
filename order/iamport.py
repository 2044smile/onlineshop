import requests

from django.conf import settings

def get_token(): # 아임포트 서브와 통신하기 위한 토큰을 받아오는 함수
    access_data = {
        'imp_key': settings.IAMPORT_KEY,
        'imp_secret': settings.IAMPORT_SECRET,
    }

    url = "https://api.iamport.kr/users/getToken"

    req = requests.post(url,data=access_data) # requests란 모듈이다. pip install requests
    access_res = req.json

    if access_res['code'] is 0:
        return access_res['response']['access_token']
    else:
        return None

def payments_prepare(order_id,amount,*args,**kwargs): # 결제를 준비하는 함수
    # 아임포트에 미리 정보를 전달하여 어떤 주문 번호로 얼마를 결제할지 미리 전달하는 역할
    access_token = get_token()
    if access_token:
        access_data = {
            'merchant_uid':order_id,
            'amount':amount
        }
        url = "https://api.iamport.kr/payments/prepare"
        headers = {
            'Authorization':access_token
        }
        req = requests.post(url, data=access_data, headers=headers)
        res = req.json()

        if res['code'] is not 0:
            raise ValueError("API 통신 오류")
    else:
        raise ValueError("토큰 오류")

def find_transcation(order_id,*args,**kwargs): # 결제가 완료 된 후에 실제 결제가 이뤄진 것이 맞는지 확인
    access_token = get_token()
    if access_token:
        url = "https://api.iamport.kr/payments/find/"+order_id

        headers = {
            'Authorization':access_token
        }

        req = requests.post(url, headers=headers)
        res = req.json()

        if res['code'] is 0:
            context = {
                'imp_id':res['response']['imp_uid'],
                'merchant_order_id':res['response']['merchant_uid'], # merchant 상인
                'amount':res['response']['amount'],
                'status':res['response']['status'],
                'type':res['response']['pay_method'],
                'receipt_url':res['response']['receipt_url'],
            }
            return context
        else:
            return None
    else:
        raise ValueError("토큰 오류")