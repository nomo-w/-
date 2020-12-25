# coding: utf-8

from aliyunsdkcore.request import CommonRequest
from aliyunsdkcore.client import AcsClient
from db.success import SuccessDB
from db.channel import ChannelDB
from functools import wraps
from flask import request
from config import *


import traceback
import requests
import hashlib
import random
import time
import json


def handle_httpresponse(data, status=-1, other={}):
    '''
    处理返回结果
    :param data: 数据
    :param status: 返回状态 0(成功) -1(不成功)
    :param other: 其他需要加入的数据
    :return: json格式的数据
    '''
    return_dic = {'data': data, 'status': Return_Statua_Code.error}
    if status == 0:
        return_dic['status'] = Return_Statua_Code.ok
    if other:
        for i in other:
            return_dic[i] = other[i]
    return json.dumps(return_dic)


def handle_api_zsq(api_path, method):
    # 处理http response装饰器
    def zsq(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if method == 'get':
                _ = f'{request.remote_addr} {method.upper()} => {api_path} : 【{kwargs["_id"]}】'
            else:
                _ = f'{request.remote_addr} {method.upper()} => {api_path} : ' \
                    f'【{request.args if method == "GET" else request.form if method == "POST" else request.data}】'
            print(_, 0, 'request', LogDefine.request_log_file.format(time.strftime("%Y-%m-%d", time.localtime())))
            try:
                resp = func(*args, **kwargs)
            except KeyError:
                # traceback.print_exc()
                resp = handle_httpresponse('参数错误!')
            except Exception as e:
                traceback.print_exc()
                # er = ";".join(traceback.format_exc().split("\n"))
                # print(f'服务器错误, 错误原因 [{er}]!!!', 2, '服务器错误')
                resp = handle_httpresponse(f'服务器错误, 错误原因 [{e}]')
            return resp
        return inner
    return zsq


def my_requests(url, method, params=None, headers=None, need_json_resp=True,
                verify=False, need_json_params=False, need_proxies=False, proxies=None):
    '''
    发送requests的请求
    :param url: 目标url
    :param headers: 请求头
    :param params: 请求参数
    :param method: 请求方法
    :param is_json: 是否返回json数据
    :param verify: ssl验证
    :param need_handle_resp: 是否需要处理数据
    :return: 返回响应参数
    '''
    try:
        data = {'url': url, 'verify': verify, 'timeout': (10, 10)}
        if params is not None:
            data['params' if method == 'get' else 'data'] = json.dumps(params) if need_json_params else params
        if need_proxies:
            data['proxies'] = proxies
        if headers is not None:
            data['headers'] = headers

        if method == 'get':
            resp = requests.get(**data)
        elif method == 'post':
            resp = requests.post(**data)

        if resp.status_code is not 200:
            print(f'请求 [{url}] 失败. 返回状态码 [{resp.status_code}]. 失败原因 [{resp.reason}]', 2, '发送request请求错误')
            return None
        return resp.json() if need_json_resp else resp.text
    except Exception as e:
        # traceback.print_exception()
        print(f'请求 [{url}] 失败. 失败原因 [{e}]', 2, '发送request请求错误')
        return None


def signature(params, secretKey=WangYi.secretKey):
    params_str = ""
    for k in sorted(params.keys()):
        params_str += str(k) + str(params[k])
    params_str += secretKey
    return hashlib.md5(params_str.encode("utf-8")).hexdigest()


def wy_send(to, yzm):
    data = {
        'secretId': WangYi.secretId,
        'businessId': WangYi.businessId,
        'version': WangYi.version,
        'timestamp': int(time.time() * 1000),
        'nonce': int(random.random() * 100000000),
        'paramType': WangYi.paramType,
        'templateId': WangYi.templateId,
        'params': json.dumps({"code": yzm}),
        'mobile': to,
    }
    data['signature'] = signature(data)
    resp = my_requests(WangYi.send_url, 'post', data)
    # {'code': 200, 'msg': 'ok', 'data': {'result': 200, 'requestId': 'a7a03b29d0c24afca1de863681b9f0e7'}}
    # {'code': 405, 'msg': 'param error', 'data': None}
    status, message, message_id, channel_type = False, '', '0', WangYi.channel_name
    if resp is not None:
        if str(resp['code']) == WangYi.return_success_code:
            if str(resp['data']['result']) == WangYi.result_success_code:
                status, message, message_id = True, 'success', resp['data']['requestId']
            else:
                message = WangYi.result_code[str(resp['data']['result'])]
        else:
            message = resp['msg']
    return status, message, message_id, channel_type


def ali_send(to, yzm):
    client = AcsClient(Ali.accessKeyID, Ali.accessKeySecret, Ali.regionId)

    req = CommonRequest()
    req.set_accept_format(Ali.format)
    req.set_domain(Ali.domain)
    req.set_method(Ali.method)
    req.set_protocol_type(Ali.protocol_type)
    req.set_version(Ali.version)
    req.set_action_name(Ali.action)

    req.add_query_param('RegionId', Ali.regionId)
    req.add_query_param('PhoneNumbers', to)
    req.add_query_param('SignName', Ali.signName)
    req.add_query_param('TemplateCode', Ali.templateCode)
    req.add_query_param('TemplateParam', {"code": yzm})

    response = client.do_action(req)
    _ = json.loads(str(response, encoding='utf-8'))
    return True if _['Code'] == Ali.return_success_code else False, _['Message'], _.get('BizId', '0'), Ali.channel_name


def dispatcher(to, yzm):
    send = random.sample([ali_send, wy_send], 1)[0]
    return send(to, yzm)


def sign_(data, charset='utf-8'):
    '''
    私钥签名,使用utf-8编码
    :param message: 需要签名的数据
    :param private_key_file: rsa私钥文件的位置
    :return: 签名后的字符串
    '''
    signature = hashlib.md5(data.encode(charset)).hexdigest()
    return signature


def verify_(signature, data, charset='utf-8'):
    '''
    公钥验签,使用utf-8编码
    :param signature: 经过签名处理的数据
    :param data: 需要验证的数据
    :param publickey_path: rsa公钥文件的位置
    :return: bool值
    '''
    sign = sign_(data, charset)
    return [False, True][sign == signature]


def get_history(channel, to, status, start, end, page):
    with SuccessDB() as db:
        data = db.get_history(channel, to, status, start, end, page)
        page_total, total = db.get_page(channel, to, status, start, end)
        data = [{'channel_name': i[0], 'to': i[1], 'yzm': i[2], 'create_time': i[3], 'description': i[4]} for i in data] if data else []
    with ChannelDB() as db:
        channel_list = db.get_channel()
    return page_total, total, data, channel_list


if __name__ == '__main__':
    data = {
        'to': '123012304324',
        'yzm': '3325'
    }
    qm = 'to123012304324yzm3325keyIYEAouewMcyUYEk35V8rHik9LkQU0C'
    a = sign_(qm)
    print(a)
    print(verify_(a, 'to123012304324yzm3325keyIYEAouewMcyUYEk35V8rHik9LkQ0C'))