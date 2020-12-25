# coding: utf-8
import os


class WangYi:
    channel_name = 'wy'
    send_url = 'https://sms.dun.163.com/v2/sendsms'
    businessId = 'xxxxxxxxxxxxxxxxxxxxxxxxx'
    secretId = 'xxxxxxxxxxxxxxxxxxxxxxxxx'
    secretKey = 'xxxxxxxxxxxxxxxxxxxxxxx'
    version = 'v2'
    paramType = 'json'
    templateId = '10840'
    return_success_code = '200'
    result_success_code = '200'
    result_code = {
        '203': 'service exception',
        '200': 'ok',
        '206': 'mobile error',
        '216': 'content error',
        '222': 'over maximum limits'
    }


class Ali:
    channel_name = 'al'
    return_success_code = 'OK'
    success_code = 'DELIVERED'
    accessKeyID = 'xxxxxxxxxxxxxxxxxxxxxxxxx'
    accessKeySecret = 'xxxxxxxxxxxxxxxxxxxxxxxx'
    templateCode = "SMS_194915791"
    signName = 'xxxxxxxxx'
    regionId = 'default'
    action = 'SendSms'
    version = '2017-05-25'
    method = 'POST'
    domain = 'dysmsapi.aliyuncs.com'
    format = 'json'
    protocol_type = 'https'
    # request_url = 'http://dybaseapi.aliyuncs.com'


class LogDefine:
    """log定义"""
    Login = 1
    Logout = 2
    Start = 3
    Stop = 4
    # del_log_time = '02:00:00'
    interval_del_time = 60 * 60
    logpath = os.path.abspath(os.path.dirname(__file__)) + '/logs'
    request_log_file = logpath + '/{}_request.log'
    log_level = {
        0: 'DEBUG',
        1: 'WARING',
        2: 'ERROR'
    }


class Return_Statua_Code:
    """返回状态定义"""
    ok = 200
    error = 500


class Sql:
    """mysql连接配置"""
    # BILL 2018-06-28 START
    host = '127.0.0.1'
    password = 'intel@123'
    port = 3306
    user = 'root'
    db = 'sms'
    max_cached = 10


class RedisSql:
    host = '127.0.0.1'
    port = 6379
    sending = 'sending'
    pending = 'pending'
    result_queue_name = "result_sms"
    db = 0


class Sign:
    key = 'IYEAouewMcyUYEk35V8rHik9LkQU0C'


class Page:
    history_limit = 25
    max_page_list = 3
