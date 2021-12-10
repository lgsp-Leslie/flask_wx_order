#!/usr/bin/env python3
# coding=utf-8
# Version:python3.6.1
# File:utils.py
# Author:LGSP_Harold
import base64
import hashlib
import json
import os
import random
import stat
import string
import uuid
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

import requests
from flask import g, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename

from apps.api.queue import QueueService
from apps.models.food_models import AccessLog, ErrorLog, User, Files, FoodSaleChangeLog
from apps.models.wx_models import Member, PayOrder, PayOrderCallbackData, PayOrderItem, OauthAccessToken
from config.conf import Config

from config.exts import db


# 判断用户是否登录
def check_login():
    cookies = request.cookies
    auth_cookie = cookies[Config.AUTH_COOKIE_NAME] if Config.AUTH_COOKIE_NAME in cookies else None
    # current_app.logger.info('auth_cookie-%s' % auth_cookie)
    if auth_cookie is None:
        return False

    auth_info = auth_cookie.split('#')
    if len(auth_info) != 2:
        return False
    try:
        user_obj = User.query.get(auth_info[1])
    except Exception as e:
        current_app.logger.info(e)
        return False

    if user_obj is None:
        return False

    if auth_info[0] != gene_auth_code(user_obj, 'user'):
        return False

    if user_obj.status != 1:
        return False

    return user_obj


# 判断小程序用户是否登录
def check_member_login():
    auth_token = request.headers.get('Authorization')

    if auth_token is None:
        return False

    auth_info = auth_token.split('#')
    if len(auth_info) != 2:
        return False
    try:
        member_obj = Member.query.get(auth_info[1])
    except Exception as e:
        current_app.logger.info(e)
        return False

    if member_obj is None:
        return False

    if auth_info[0] != gene_auth_code(member_obj, 'member'):
        return False

    if member_obj.status != 1:
        return False

    return member_obj


# 格式化手机号
def mobile_format(mobile):
    mobile = str(mobile)
    mobile = mobile.replace(mobile[3:8], '****')
    return mobile


# 判断是否是数字
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


# 产生随机salt
def random_salt():
    return ''.join(random.sample(string.ascii_letters + string.digits, 9))


# 加密密码（MD5+salt）
def gene_pwd(pwd, salt):
    m = hashlib.md5()
    _str = "%s--%s" % (base64.encodebytes(pwd.encode('utf-8')), salt)
    m.update(_str.encode('utf-8'))
    return m.hexdigest()


# 产生授权码给cookie使用
def gene_auth_code(obj, _type):
    m = hashlib.md5()
    _str = None
    if _type == 'user':
        _str = '%s-%s-%s-%s' % (obj.id, obj.login_name, obj.login_pwd, obj.login_salt)
    if _type == 'member':
        _str = '%s-%s-%s' % (obj.id, obj.login_salt, obj.status)
    m.update(_str.encode('utf-8'))
    return m.hexdigest()


# 统一渲染方法
def ops_render(template, context=None):
    if context is None:
        context = {}
    if 'current_user' in g:
        context['current_user'] = g.current_user
    return render_template(template, **context)


# 添加访问记录
def add_access_log():
    access_obj = AccessLog()
    access_obj.target_url = request.url
    access_obj.referer_url = request.referrer
    access_obj.ip = request.remote_addr
    access_obj.query_params = json.dumps(request.values.to_dict())

    if 'current_user' in g and g.current_user is not None:
        access_obj.uid = g.current_user.id
    access_obj.ua = request.headers.get('User-Agent')

    db.session.add(access_obj)
    db.session.commit()
    return True


# 添加错误记录
def add_error_log(err):
    error_obj = ErrorLog()
    error_obj.target_url = request.url
    error_obj.referer_url = request.referrer
    error_obj.ip = request.remote_addr
    error_obj.query_params = json.dumps(request.values.to_dict())
    error_obj.content = err
    if 'current_user' in g and g.current_user is not None:
        error_obj.uid = g.current_user.id
    error_obj.ua = request.headers.get('User-Agent')
    db.session.add(error_obj)
    db.session.commit()
    return True


# 获取微信openid
def get_wechat_openid(js_code):
    url = 'https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code'.format(
        Config.WX_APPID, Config.WX_SECRET, js_code)

    doc = requests.get(url=url)
    res = json.loads(doc.text)
    openid = None
    if 'openid' in res:
        openid = res['openid']
    return openid


# 返回图片地址
def build_image_url(path):
    url = Config.DOMAIN + '/' + Config.UPLOAD['prefix_url'] + path
    return url


# 文件上传本地
def upload_file(file_storage):
    resp = {'code': 200, 'msg': '操作成功！', 'data': {}}
    filename = secure_filename(file_storage.filename)
    ext = filename.rsplit('.', 1)[1]
    if ext not in Config.UPLOAD['ext']:
        resp['code'] = -1
        resp['msg'] = '不允许的扩展类型文件'
        return resp

    file_dir = datetime.now().strftime('%Y%m%d')
    save_dir = Config.UPLOAD['prefix_path'] + file_dir

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        os.chmod(save_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IRWXO)

    file_name = str(uuid.uuid4().hex) + '.' + ext
    file_storage.save('{0}/{1}'.format(save_dir, file_name))

    add_file_obj = Files()
    add_file_obj.file_key = file_dir + '/' + file_name
    db.session.add(add_file_obj)
    db.session.commit()

    resp['data'] = {
        'file_key': add_file_obj.file_key
    }

    return resp


# 上传图片
def upload_image():
    resp = {
        'state': 'SUCCESS',
        'url': '',
        'title': '',
        'original': ''
    }
    file_target = request.files
    upfile = file_target['upfile'] if 'upfile' in file_target else None
    if upfile is None:
        resp['state'] = '上传失败'
        return jsonify(resp)

    ret = upload_file(upfile)
    if ret['code'] != 200:
        resp['state'] = '上传失败：' + ret['msg']

    resp['url'] = build_image_url(ret['data']['file_key'])

    return jsonify(resp)


# 富文本图片管理
def list_image():
    resp = {'state': 'SUCCESS', 'list': [], 'start': 0, 'total': 0}

    req = request.values
    start = int(req['start']) if 'start' in req else 0
    page_size = int(req['size']) if 'size' in req else 20

    query = Files.query
    if start > 0:
        query = query.filter(Files.id < start)

    file_list = query.order_by(-Files.id).limit(page_size).all()

    print('file_list,', file_list)

    files = []
    if file_list:
        for item in file_list:
            files.append({'url': build_image_url(item.file_key)})
            start = item.id

    resp['list'] = files
    resp['start'] = start
    resp['total'] = len(files)

    return jsonify(resp)


# 生成随机字符串
def get_nonce_str():
    return str(uuid.uuid4().hex)


# 生成微信支付签名
def create_sign(pay_data, merchant_key):
    stringA = '&'.join(['{0}={1}'.format(k, pay_data.get(k)) for k in sorted(pay_data)])

    stringSignTemp = '{0}&key={1}'.format(stringA, merchant_key)
    sign = hashlib.md5(stringSignTemp.encode('utf-8')).hexdigest()
    return sign.upper()


# 字典转xml
def dict_to_xml(dict_data):
    xml = ['<xml>']
    for k, v in dict_data.items():
        xml.append('<{0}>{1}</{0}>'.format(k, v))
    xml.append('</xml>')
    return ''.join(xml)


# xml转字典
def xml_to_dict(xml_data):
    xml_dict = {}
    root = ET.fromstring(xml_data)
    for child in root:
        xml_dict[child.tag] = child.text

    return xml_dict


# 获取微信支付信息
def get_wx_pay_info(pay_data=None, merchant_key=None):
    sign = create_sign(pay_data, merchant_key)
    print('utils.py', sign)
    pay_data['sign'] = sign
    print('utils.py', pay_data)
    xml_data = dict_to_xml(pay_data)
    url = 'https://api.mch.weixin.qq.com/v3/pay/transactions/jsapi'
    headers = {
        'Content-Type': 'application/xml'
    }
    r = requests.post(url=url, data=xml_data.encode('utf-8'), headers=headers)
    r.encoding = 'utf-8'
    current_app.logger.info(r.text)
    if r.status_code == 200:
        prepay_id = xml_to_dict(r.text).get('prepay_id')
        pay_sign_data = {
            'appId': pay_data.get('appid'),
            'timeStamp': pay_data.get('out_trade_no'),
            'nonceStr': pay_data.get('nonce_str'),
            'package': 'prepay_id={0}'.format(prepay_id),
            'signType': 'MD5',
        }
        pay_sign = create_sign(pay_sign_data, merchant_key)
        pay_sign_data.pop('appId')
        pay_sign_data['paySign'] = pay_sign
        pay_sign_data['prepay_id'] = prepay_id

        return pay_sign_data

    return False


# 订单成功
def order_success(pay_oder_id=0, params=None):
    try:
        pay_order_info = PayOrder.query.get(pay_oder_id)
        if not pay_order_info or pay_order_info.status not in [-8, -7]:
            pay_order_info.pay_sn = params['pay_sn'] if 'pay_sn' in params else ''
            pay_order_info.status = 1
            pay_order_info.express_status = -7
            pay_order_info.pay_time = datetime.now()

            # 售卖历史
            pay_order_items = PayOrderItem.query_filter_by(pay_oder_id=pay_oder_id).all()
            for item in pay_order_items:
                tmp_model_sale_log = FoodSaleChangeLog()
                tmp_model_sale_log.food_id = item.food_id
                tmp_model_sale_log.quantity = item.quantity
                tmp_model_sale_log.price = item.price
                tmp_model_sale_log.member_id = item.member_id
                db.session.add(tmp_model_sale_log)

            db.session.commit()
    except Exception as e:
        db.session.rollback()
        return False

    QueueService.add_queue('pay', {
        'member_id': pay_order_info.member_id,
        'pay_order_id': pay_order_info.id
    })


# 将微信回调的结果放入记录表
def add_pay_callback_data(pay_order_id=0, _type='pay', data=''):
    model_callback = PayOrderCallbackData()
    model_callback.pay_order_id = pay_order_id
    if _type == 'pay':
        model_callback.pay_data = data
        model_callback.refund_data = ''
    else:
        model_callback.pay_data = ''
        model_callback.refund_data = data

    db.session.add(model_callback)
    db.session.commit()
    return True



