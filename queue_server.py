from db import pending, failed, success, channel
from multiprocessing import Process
from db import myredis
from config import *

import json
import time
import log


def handle_success(to, message_id, yzm='', channel_id=0, is_update=True):
    if is_update:
        with pending.PendingDB()as db:
            return db.update(message_id, 'success', to)
    else:
        with success.SuccessDB() as db:
            db.add(to, yzm, channel_id, message_id)


def handle_failed(to, yzm, channel_id, message, message_id, is_update=False):
    if is_update:
        with pending.PendingDB() as db:
            db.update(message_id, message, to)
    else:
        with failed.FailedDB() as db:
            db.add(to, yzm, channel_id, message, message_id)


def handle_pending(to, yzm, channel_id, message_id):
    with pending.PendingDB() as db:
        db.add(to, yzm, channel_id, message_id)


def queue_pending_forever():
    while True:
        num = myredis.mlen(RedisSql.pending)
        if num > 0:
            for n in range(num):
                try:
                    data = json.loads(myredis.mpop(RedisSql.pending))
                    print(f'处理pending数据：{data}', 0, '处理pending数据')
                    channel_type = data.pop('channel_type')
                    with channel.ChannelDB() as db:
                        channel_id, need_report = db.get_channel_info(channel_type=channel_type)
                    if data['status']:
                        if need_report:
                            handle_pending(data['to'], data['yzm'], channel_id, data['message_id'])
                        else:
                            handle_success(data['to'], data['message_id'], data['yzm'], channel_id, is_update=False)
                    else:
                        handle_failed(data['to'], data['yzm'], channel_id, data['message'], data['message_id'])
                except Exception as e:
                    print(f'处理pending短信失败, 失败原因[{e}]', 2, '处理pending短信错误')
        # else:
        #     time.sleep(30)


def queue_result_forever():
    while True:
        num = myredis.mlen(RedisSql.result_queue_name)
        if num > 0:
            for n in range(num):
                try:
                    data = json.loads(myredis.mpop(RedisSql.result_queue_name))
                    print(f'处理短信数据：{data}', 0, '处理短信结果')
                    channel_type = data.pop('channel_type')
                    with channel.ChannelDB() as db:
                        channel_id, need_report = db.get_channel_info(channel_type=channel_type)
                    if data['status']:
                        resp = handle_success(data['to'], data['message_id'])
                    else:
                        resp = handle_failed(data['to'], data['yzm'], channel_id, data['message'], data['message_id'], is_update=True)
                    if not resp:
                        if data.get('count', 0) < 3:
                            data['count'] = data.get('count', 0) + 1
                            myredis.mpush(json.dumps(data), RedisSql.result_queue_name)
                        else:
                            print(f'更新短信结果失败, 当前数据[{data}]', 2, '更新短信结果失败')
                except Exception as e:
                    print(f'处理短信结果失败, 失败原因[{e}]', 2, '处理短信结果错误')
        time.sleep(60)


if __name__ == '__main__':
    log.init()
    # 将发送中短信写入mysql
    Process(target=queue_pending_forever, name='queue_pending_server').start()
    # 将短信结果写入mysql
    queue_result_forever()
