import requests
from config import WangYi
import time
import random
from api import signature

url = 'https://sms.dun.163.com/v2/verifysms'
data = {
    'requestId': '8cf20c21de6248769c9bd6f522e7be4e',
    'code': '5362',
    'secretId': WangYi.secretId,
    'businessId': WangYi.businessId,
    'version': WangYi.version,
    'timestamp': int(time.time() * 1000),
    'nonce': int(random.random() * 100000000)
}
data['signature'] = signature(data)
print(data)
resp = requests.post(url, data=data)
print(resp.json())
