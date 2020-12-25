# coding: utf-8


from flask import Flask, request, render_template
from flask_cors import CORS
from db import myredis
from config import *

import json
import api
import log

app = Flask('web')
CORS(app, supports_credentials=True)
app.secret_key = 'ABCAz47j22AA#R~X@H!jLwf/A'
log.init()


@app.route('/api/result/<channel>', methods=['post'])
@api.handle_api_zsq('/api/result', 'post')
def result(channel):
    #[{
    #     "send_time":"2020-07-03 12:53:10",
    #     "report_time":"2020-07-03 12:53:16",
    #     "success":true,
    #     "err_msg":"用户接收成功",
    #     "err_code":"DELIVERED",
    #     "phone_number":"13031046676",
    #     "sms_size":"1",
    #     "biz_id":"706715193751989145^0"
    # }]
    if channel == Ali.channel_name:
        data = json.loads(request.data.decode())
        for i in data:
            myredis.mpush(json.dumps({
                'to': i['phone_number'],
                'status': 'SUCCESS' if i['err_code'] == Ali.success_code else i['err_code'],
                'message': i['err_msg'],
                'message_id': i['biz_id'],
                'channel_type': Ali.channel_name
            }), RedisSql.result_queue_name)
        resp = json.dumps({"code": 0, "msg": "成功"})
    else:
        resp = '<title>404 Not Found</title><h1>Not Found</h1>'
    return resp


@app.route('/api/send', methods=['post'])
@api.handle_api_zsq('/api/send', 'post')
def send():
    data = request.data.decode()
    if data:
        data = json.loads(data)
        to, yzm, signature = data['to'], data['yzm'], data['signature']
        if api.verify_(signature, f'to{to}yzm{yzm}key{Sign.key}'):
            myredis.mpush(json.dumps({'to': to, 'yzm': yzm}), RedisSql.sending)
            return api.handle_httpresponse('ok', 0)
        return api.handle_httpresponse('验签失败!')
    return api.handle_httpresponse('参数错误!')


@app.route("/<_id>")
@api.handle_api_zsq('/', 'GET')
def index_id(_id):
    return render_template('404.html'), 404


@app.route("/")
@api.handle_api_zsq('/', 'GET')
def index():
    status, _time, page = request.args.get('status', '0'), request.args.get('time', ''), request.args.get('page', 1)
    channel, to, pages = request.args.get('channel', '0'), request.args.get('to', ''), request.args.get('turn_page')
    page = int(page) if page else 1
    if pages == '上一页':
        if page > 1:
            pages, page = page - 2, page - 1
        else:
            pages, page = 0, 1
    elif pages == '下一页':
        if int(page) > 0:
            pages, page = page, page + 1
        else:
            pages, page = 0, 1
    else:
        pages, page = page - 1 if page else 0, 1 if page < 1 else page
    page_total, total, data, channel_list = api.get_history(channel, to, status, _time, _time, pages)
    return render_template("index.html", sms_list=data, status=status, page=page, total=total, _time=_time,
                           channel_list=channel_list, select_channel=channel, to=to, page_total=page_total)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, threaded=True)
