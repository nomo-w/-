from api import dispatcher
from db import myredis
from config import *

import json
import log


def get_one():
    # 从redis里弹出一条
    """
    :return: (user, to_number, text) or (None, None, None)
    """
    try:
        r = myredis.mpop(RedisSql.sending)
        return json.loads(r) if r else None
    except Exception as e:
        print(f'从redis拿出短信失败: {e}', 2, 'redis错误')
    return None


def send_forever():
    while True:
        if myredis.mlen(RedisSql.sending):
            data = get_one()
            try:
                print(f'发送短信 ## [{data["yzm"]}] ==> [{data["to"]}]', 0, '发送短信')
                status, message, message_id, channel_type = dispatcher(**data)
                # status, message, message_id, channel_type = True, 'aaa', 'aaa', 'wy'
                print(f'短信商返回值 ## 信息:[{message}] | 状态:[{status}]', 0, '发送短信返回值')
                myredis.mpush(json.dumps({
                    'to': data['to'],
                    'yzm': data['yzm'],
                    'status': status,
                    'channel_type': channel_type,
                    'message': message,
                    'message_id': message_id
                }), RedisSql.pending)
            except Exception as e:
                myredis.mpush(json.dumps({
                    'to': data['to'],
                    'yzm': data['yzm'],
                    'status': False,
                    'channel_type': 'al',
                    'message': f'错误{e}',
                    'message_id': -11
                }), RedisSql.pending)
                print(f'发送短信失败, 失败原因[{e}]', 2, '发送短信错误')


if __name__ == '__main__':
    log.init()
    send_forever()
