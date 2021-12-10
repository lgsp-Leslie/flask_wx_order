#!/usr/bin/env python3
# coding=utf-8
# Author:LGSP_Harold
import decimal
import json
import uuid
from datetime import datetime

from flask import Blueprint, request, jsonify, url_for, g, current_app
from sqlalchemy import or_

from apps.api.order import close_order
from apps.models.food_models import FoodCat, Food, FoodStockChangeLog
from apps.models.wx_models import OauthMemberBind, Member, ShareHistory, MemberCart, PayOrder, PayOrderItem, \
    MemberComments
from apps.utils.utils import random_salt, get_wechat_openid, gene_auth_code, get_wx_pay_info, get_nonce_str, \
    xml_to_dict, create_sign, dict_to_xml, order_success, add_pay_callback_data
from config.conf import Config
from config.exts import db

api_bp = Blueprint('api_wx', __name__)


@api_bp.route('/')
@api_bp.route('/index')
def index():
    return 'mina'


# 微信登录
@api_bp.route('/member/login', methods=['POST'])
def login():
    resp = {'code': 200, 'msg': '登录成功', 'data': {}}

    req = request.values
    # current_app.logger.info(req)
    js_code = req['code'] if 'code' in req else ''
    if not js_code or len(js_code) < 1:
        resp['code'] = -1
        resp['msg'] = '缺少code！'
        return jsonify(resp)

    openid = get_wechat_openid(js_code)
    if openid is None:
        resp['code'] = -1
        resp['msg'] = '调用微信出错！'
        return jsonify(resp)

    oauth_obj = OauthMemberBind.query.filter_by(openid=openid).first()
    if not oauth_obj:
        nickname = req['nickName'] if 'nickName' in req else ''
        sex = req['gender'] if 'gender' in req else 0
        avatar_url = req['avatarUrl'] if 'avatarUrl' in req else ''

        member_obj = Member()
        member_obj.nickname = nickname
        member_obj.sex = sex
        member_obj.avatar = avatar_url
        member_obj.login_salt = random_salt()
        # member_obj.reg_ip = ''
        db.session.add(member_obj)
        db.session.commit()

        bind_obj = OauthMemberBind()
        bind_obj.member_id = member_obj.id
        # bind_obj.type = ''
        bind_obj.openid = openid
        db.session.add(bind_obj)
        db.session.commit()

        oauth_obj = bind_obj

    member_obj = Member.query.get(oauth_obj.member_id)

    _gene_auth_code = gene_auth_code(member_obj, 'member')
    if _gene_auth_code is None:
        resp['code'] = -1
        resp['msg'] = 'geneAuthCode不能为None！'
        return jsonify(resp)

    token = '%s#%s' % (_gene_auth_code, member_obj.id)

    resp['data'] = {'token': token}
    return jsonify(resp)


# 注册授权验证
@api_bp.route('/member/check-reg', methods=['POST'])
def check_reg():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values
    js_code = req['code'] if 'code' in req else ''
    if not js_code or len(js_code) < 1:
        resp['code'] = -1
        resp['msg'] = '需要code',
        return jsonify(resp)

    openid = get_wechat_openid(js_code)
    if openid is None:
        resp['code'] = -1
        resp['msg'] = '调用微信出错！'
        return jsonify(resp)

    oauth_obj = OauthMemberBind.query.filter_by(openid=openid).first()
    if not oauth_obj:
        resp['code'] = -1
        resp['msg'] = '未绑定账号！'
        return jsonify(resp)

    member_obj = Member.query.get(oauth_obj.member_id)
    if not member_obj:
        resp['code'] = -1
        resp['msg'] = '未查询到绑定信息！'
        return jsonify(resp)

    _gene_auth_code = gene_auth_code(member_obj, 'member')
    if _gene_auth_code is None:
        resp['code'] = -1
        resp['msg'] = 'geneAuthCode不能为None！'
        return jsonify(resp)

    token = '%s#%s' % (_gene_auth_code, member_obj.id)
    resp['data'] = {
        'token': token
    }

    return jsonify(resp)


# 分享转发
@api_bp.route('/member/share', methods=['POST'])
def member_share():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values
    url = req['url'] if 'url' in req else ''
    device = req['device'] if 'device' in req else ''
    member_obj = g.member_obj
    if not member_obj:
        resp['code'] = -1
        resp['msg'] = '请先登录！'
        return jsonify(resp)

    share_obj = ShareHistory()
    share_obj.member_id = member_obj.id
    share_obj.share_url = url
    share_obj.device = device
    db.session.add(share_obj)
    db.session.commit()

    return jsonify(resp)


# 食物首页
@api_bp.route('/food/index')
def food_index():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    cat_list = FoodCat.query.filter_by(status=1).order_by(-FoodCat.weight).all()
    data_cat_list = [{
        'id': 0,
        'name': '全部'
    }]
    if cat_list:
        for item in cat_list:
            tmp_data = {
                'id': item.id,
                'name': item.name
            }
            data_cat_list.append(tmp_data)
        resp['data']['cat_list'] = data_cat_list

    food_list = Food.query.filter_by(status=1).order_by(Food.total_count.desc()).limit(3).all()

    data_food_list = []
    if food_list:
        for item in food_list:
            tmp_data = {
                'id': item.id,
                'pic_url': Config.DOMAIN + url_for('static', filename='upload/' + item.main_image)
            }
            data_food_list.append(tmp_data)
    resp['data']['banner_list'] = data_food_list

    return jsonify(resp)


# 筛选、搜索
@api_bp.route('/food/search')
def food_search():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values
    c_id = int(req['cat_id']) if 'cat_id' in req else 0
    mix_kw = req['mix_kw'] if 'mix_kw' in req else ''
    page = int(req['page']) if 'page' in req else 1

    if page < 1:
        p = 1

    offset = (page - 1) * Config.PER_PAGE

    query = Food.query.filter_by(status=1)
    if c_id > 0:
        query = query.filter(Food.cat_id == c_id)
    if mix_kw:
        rule = or_(Food.name.contains('%s' % mix_kw), Food.tags.contains('%s' % mix_kw))
        query = query.filter(rule)
    food_list = query.order_by(-Food.total_count, -Food.id).offset(offset).limit(Config.PER_PAGE).all()
    data_food_list = []
    if food_list:
        for item in food_list:
            tmp_data = {
                'id': item.id,
                'name': item.name,
                'price': str(item.price),
                'min_price': str(item.price),
                'pic_url': Config.DOMAIN + url_for('static', filename='upload/' + item.main_image)
            }
            data_food_list.append(tmp_data)

    resp['data']['list'] = data_food_list
    resp['data']['has_more'] = 0 if len(data_food_list) < Config.PER_PAGE else 1

    return jsonify(resp)


# 食物详情页
@api_bp.route('/food/info')
def food_info():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values
    f_id = req['food_id'] if 'food_id' in req else 0

    info = Food.query.get(f_id)
    if not info or info.status == 0:
        resp['code'] = -1
        resp['msg'] = '美食不存在'
        return jsonify(resp)

    member_obj = g.member_obj
    cart_number = 0
    if member_obj:
        cart_number = MemberCart.query.filter_by(member_id=member_obj.id).count()

    resp['data']['info'] = {
        'id': info.id,
        'name': info.name,
        'summary': info.summary,
        'total_count': info.total_count,
        'comment_count': info.comment_count,
        'main_image': Config.DOMAIN + url_for('static', filename='upload/' + info.main_image),
        'price': info.price,
        'stock': info.stock,
        'pics': [Config.DOMAIN + url_for('static', filename='upload/' + info.main_image)]
    }

    resp['data']['cart_number'] = cart_number

    return jsonify(resp)


# 购物车
@api_bp.route('/food/cart', methods=['GET', 'POST', 'DELETE'])
def food_cart():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    if request.method == 'GET':
        member_obj = g.member_obj
        if not member_obj:
            resp['code'] = -1
            resp['msg'] = '未登录！'
            return jsonify(resp)
        cart_list = MemberCart.query.filter_by(member_id=member_obj.id).all()

        data_cart_list = []

        if cart_list:
            for item in cart_list:
                tmp_data = {
                    'id': item.id,
                    'food_id': item.food_id,
                    'number': item.quantity,
                    'name': item.food.name,
                    'price': item.food.price,
                    'pic_url': Config.DOMAIN + url_for('static', filename='upload/' + item.food.main_image),
                    'active': True
                }
                data_cart_list.append(tmp_data)

        resp['data']['list'] = data_cart_list

        return jsonify(resp)

    if request.method == 'POST':
        req = request.values
        f_id = int(req['id']) if 'id' in req else 0
        number = int(req['number']) if 'number' in req else 0
        if f_id < 1 or number < 1:
            resp['code'] = -1
            resp['msg'] = '添加购物车失败'
            return jsonify(resp)

        member_obj = g.member_obj
        if not member_obj:
            resp['code'] = -1
            resp['msg'] = '添加购物车失败'
            return jsonify(resp)

        food_obj = Food.query.get(f_id)
        if not food_obj:
            resp['code'] = -1
            resp['msg'] = '添加购物车失败'
            return jsonify(resp)

        if food_obj.stock < number:
            resp['code'] = -1
            resp['msg'] = '库存不足'
            return jsonify(resp)

        cart_obj = MemberCart.query.filter_by(food_id=f_id, member_id=member_obj.id).first()

        if not cart_obj:
            cart_obj = MemberCart()
            cart_obj.member_id = member_obj.id
        cart_obj.food_id = f_id
        cart_obj.quantity = number
        db.session.add(cart_obj)
        db.session.commit()

        return jsonify(resp)

    if request.method == 'DELETE':
        req = request.values
        params_goods = req['goods'] if 'goods' in req else None
        items = []

        if params_goods:
            # 转换成json
            items = json.loads(params_goods)
        if not items or len(items) < 1:
            return jsonify(resp)

        member_obj = g.member_obj

        if not member_obj or member_obj.id < 1:
            resp['code'] = -1
            resp['msg'] = '请登录!'
            return jsonify(resp)

        for item in items:
            MemberCart.query.filter_by(food_id=item['id'], member_id=member_obj.id).delete()
        db.session.commit()
        return jsonify(resp)


@api_bp.route('/food/get/order', methods=['POST'])
def food_get_order():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values
    _type = req['type'] if 'type' in req else ''
    if request.method == 'POST':
        params_goods = req['goods'] if 'goods' in req else None
        member_obj = g.member_obj
        params_goods_list = []

        if params_goods:
            params_goods_list = json.loads(params_goods)

        food_dic = {}
        for item in params_goods_list:
            food_dic[item['id']] = item['number']

        food_ids = food_dic.keys()
        food_list = Food.query.filter(Food.id.in_(food_ids)).all()
        data_food_list = []
        freight_price = pay_price = decimal.Decimal(0.00)
        if food_list:
            for item in food_list:
                tmp_data = {
                    'id': item.id,
                    'name': item.name,
                    'price': item.price,
                    'pic_url': Config.DOMAIN + url_for('static', filename='upload/' + item.main_image),
                    'number': food_dic[item.id]
                }
                pay_price = pay_price + item.price * int(food_dic[item.id])
                data_food_list.append(tmp_data)

        default_address = {
            'name': '2',
            'mobile': '2',
            'address': 's'
        }
        resp['data']['food_list'] = data_food_list
        resp['data']['pay_price'] = pay_price
        resp['data']['yun_price'] = freight_price
        resp['data']['total_price'] = pay_price + freight_price
        resp['data']['default_address'] = default_address

        return jsonify(resp)


@api_bp.route('/food/order', methods=['POST'])
def food_order():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values
    _type = req['type'] if 'type' in req else ''
    if request.method == 'POST':
        params_goods = req['goods'] if 'goods' in req else None

        items = []
        if params_goods:
            items = json.loads(params_goods)

        if len(items) < 1:
            resp['code'] = -1
            resp['msg'] = '下单失败，没有选中商品'
            return jsonify(resp)

        member_obj = g.member_obj
        if not member_obj:
            resp['code'] = -1
            resp['msg'] = '登录失效，请重新登录！'
            return jsonify(resp)

        pay_price = decimal.Decimal(0.00)

        continue_cnt = 0
        foods_id = []

        for item in items:
            if decimal.Decimal(item['price']) < 0:
                continue_cnt += 1
                continue
            pay_price = pay_price + decimal.Decimal(item['price']) * int(item['number'])
            foods_id.append(item['id'])

        if continue_cnt >= len(items):
            resp['code'] = -1
            resp['msg'] = '商品items为空！'
            return jsonify(resp)

        freight_price = req['yun_price'] if 'yun_price' in req else 0
        note = req['note'] if 'note' in req else ''
        freight_price = decimal.Decimal(freight_price)
        total_price = pay_price + freight_price

        # 并发处理（互斥锁：悲观锁、乐观锁），悲观锁
        try:
            tmp_food_list = db.session.query(Food).filter(Food.id.in_(foods_id)).with_for_update().all()

            tmp_food_stock_mapping = {}
            for item in tmp_food_list:
                tmp_food_stock_mapping[item.id] = item.stock

            pay_order_obj = PayOrder()
            pay_order_obj.order_sn = str(uuid.uuid4().hex) + datetime.now().strftime('%Y%m%d%H%M%S')
            pay_order_obj.member_id = member_obj.id
            pay_order_obj.total_price = total_price
            pay_order_obj.freight_price = freight_price
            pay_order_obj.pay_price = pay_price
            pay_order_obj.note = note
            pay_order_obj.status = -8
            pay_order_obj.express_status = -8

            db.session.add(pay_order_obj)
            db.session.flush()

            for item in items:
                tmp_left_stock = tmp_food_stock_mapping[item['id']]
                if int(item['number']) > int(tmp_left_stock):
                    raise Exception('您购买的美食超过库存量了。当前剩余：%s'.format(tmp_left_stock))
                tmp_ret = Food.query.get(item['id'])

                if not tmp_ret:
                    raise Exception('下单失败，请重新下单！')

                tmp_ret.stock = int(tmp_left_stock) - int(item['number'])

                tmp_pay_item = PayOrderItem()
                tmp_pay_item.pay_order_id = pay_order_obj.id
                tmp_pay_item.member_id = member_obj.id
                tmp_pay_item.quantity = item['number']
                tmp_pay_item.price = item['price']
                tmp_pay_item.food_id = item['id']
                tmp_pay_item.note = note
                db.session.add(tmp_pay_item)

                stock_change_obj = FoodStockChangeLog()
                stock_change_obj.food_id = item['id']
                # todo  负号问题
                stock_change_obj.unit = int(-item['number'])

                stock_change_obj.total_stock = int(tmp_left_stock) - int(item['number'])
                stock_change_obj.note = '在线购买！'
                db.session.add(stock_change_obj)

                if _type == 'cart':
                    MemberCart.query.filter_by(member_id=member_obj.id, food_id=item['id']).delete()

            db.session.commit()
            resp['data'] = {
                'id': pay_order_obj.id,
                'order_sn': pay_order_obj.order_sn,
                'total_price': total_price
            }

        except Exception as e:
            db.session.rollback()
            current_app.logger.info(e)
            resp['code'] = -1
            resp['msg'] = '下单失败，请重新下单-2！'
            return jsonify(resp)

        return jsonify(resp)


@api_bp.route('/my/order', methods=['GET', 'POST'])
def my_order_list():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    member_obj = g.member_obj
    if not member_obj:
        resp['code'] = -1
        resp['msg'] = '未登录！'
        return jsonify(resp)
    req = request.values
    if request.method == 'POST':
        status = int(req['status']) if 'status' in req else 0

        query = PayOrder.query.filter_by(member_id=member_obj.id)

        if status == -8:
            # 等待付款
            query = query.filter(PayOrder.status == -8)
        elif status == -7:
            # 待发货
            query = query.filter(PayOrder.status == 1, PayOrder.express_status == -7, PayOrder.comment_status == 0)
        elif status == -6:
            # 待确认
            query = query.filter(PayOrder.status == 1, PayOrder.express_status == -6, PayOrder.comment_status == 0)
        elif status == -5:
            # 待评价
            query = query.filter(PayOrder.status == 1, PayOrder.express_status == 1, PayOrder.comment_status == 0)
        elif status == 1:
            # 已完成
            query = query.filter(PayOrder.status == 1, PayOrder.express_status == 1, PayOrder.comment_status == 1)
        elif status == 0:
            # 已关闭
            query = query.filter(PayOrder.status == 0)

        pay_order_list = query.order_by(PayOrder.id.desc()).all()

        data_pay_order_list = []
        if pay_order_list:
            pay_order_ids = []
            for item in pay_order_list:
                if not hasattr(item, 'id'):
                    break
                if getattr(item, 'id') in pay_order_ids:
                    continue
                pay_order_ids.append(getattr(item, 'id'))
            pay_order_item_list = PayOrderItem.query.filter(PayOrderItem.pay_order_id.in_(pay_order_ids)).all()

            food_ids = []
            for item in pay_order_item_list:
                if not hasattr(item, 'food_id'):
                    break
                if getattr(item, 'food_id') in food_ids:
                    continue
                food_ids.append(getattr(item, 'food_id'))

            food_map = {}
            query_food = Food.query
            if food_ids and len(food_ids) > 0:
                query_food = query_food.filter(Food.id.in_(food_ids))

            _list = query_food.all()
            if not _list:
                return food_map
            for item in _list:
                if not hasattr(item, 'id'):
                    break
                if getattr(item, 'id') not in food_map:
                    food_map[getattr(item, 'id')] = []

                food_map[getattr(item, 'id')].append(item)

            pay_order_item_map = {}
            if pay_order_item_list:
                for item in pay_order_item_list:
                    if item.pay_order_id not in pay_order_item_map:
                        pay_order_item_map[item.pay_order_id] = []
                    tmp_food_info = food_map[item.food_id]
                    pay_order_item_map[item.pay_order_id].append({
                        'id': item.id,
                        'food_id': item.food_id,
                        'quantity': item.quantity,
                        'pic_url': Config.DOMAIN + url_for('static', filename='upload/') + tmp_food_info[0].main_image,
                        'name': tmp_food_info[0].name
                    })
            for item in pay_order_list:
                tmp_data = {
                    'status': item.pay_status,
                    'status_desc': item.status_desc,
                    'date': item.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'order_number': item.order_number,
                    'order_sn': item.order_sn,
                    'note': item.note,
                    'total_price': str(item.total_price),
                    'goods_list': pay_order_item_map[item.id]
                }
                data_pay_order_list.append(tmp_data)

        resp['data']['pay_order_list'] = data_pay_order_list

        return jsonify(resp)


@api_bp.route('/order/pay', methods=['GET', 'POST'])
def order_pay():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values
    member_obj = g.member_obj

    if request.method == 'POST':
        order_sn = req['order_sn'] if 'order_sn' in req else ''
        pay_order_obj = PayOrder.query.filter_by(order_sn=order_sn).first()
        if not pay_order_obj:
            resp['code'] = -1
            resp['msg'] = '系统繁忙，请稍后再试！'
            return jsonify(resp)

        oauth_bind_info = OauthMemberBind.query.filter_by(member_id=member_obj.id).first()
        if not oauth_bind_info:
            resp['code'] = -1
            resp['msg'] = '系统繁忙，请稍后再试'
            return jsonify(resp)

        notify_url = Config.DOMAIN + Config.WX_CALLBACK_URL

        data = {
            'appid': Config.WX_APPID,
            'mch_id': Config.WX_MCH_ID,
            'nonce_str': get_nonce_str(),
            'body': '订餐',
            'out_trade_no': pay_order_obj.order_sn,
            'total_fee': int(pay_order_obj.total_price * 100),
            'notify_url': notify_url,
            'trade_type': 'JSAPI',
            'openid': oauth_bind_info.openid
        }
        pay_info = get_wx_pay_info(data, Config.WX_PAYKEY)

        if pay_info is False:
            resp['code'] = -1
            resp['msg'] = '服务器繁忙！'
            return jsonify(resp)

        pay_order_obj.prepay_id = pay_info['prepay_id']

        db.session.commit()

        resp['data']['pay_info'] = pay_info

        return jsonify(resp)


@api_bp.route('/order/callback', methods=['POST'])
def order_callback():
    result_data = {
        'return_code': 'SUCCESS',
        'return_msg': 'OK',
    }
    header = {
        'Content-Type': 'application/xml'
    }
    callback_data = xml_to_dict(request.data)
    current_app.logger.info(callback_data)
    sign = callback_data['sign']
    callback_data.pop('sign')

    gene_sign = create_sign(callback_data)
    current_app.logger.info(gene_sign)

    if sign != gene_sign:
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return dict_to_xml(result_data), header

    order_sn = callback_data['out_trade_no']
    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn).first()

    if not pay_order_info:
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return dict_to_xml(result_data), header

    if int(pay_order_info.total_price * 100) != int(callback_data['total_fee']):
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return dict_to_xml(result_data), header

    if pay_order_info.status == 1:
        return dict_to_xml(result_data), header

    target_pay = order_success(pay_oder_id=pay_order_info.id, params={'pay_sn': callback_data['transaction_id']})

    # 将微信回调的结果放入记录表
    result = add_pay_callback_data(pay_order_id=pay_order_info.id, data=request.data)

    return dict_to_xml(result_data), header


@api_bp.route('/order/ops', methods=['GET', 'POST'])
def order_ops():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values

    member_obj = g.member_obj
    order_sn = req['order_sn'] if 'order_sn' in req else ''
    act = req['act'] if 'act' in req else ''

    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn, member_id=member_obj.id).first()
    if not pay_order_info:
        resp['code'] = -1
        resp['msg'] = '系统繁忙，稍后再试'
        return jsonify(resp)
    if act == 'cancel':
        ret = close_order(pay_order_id=pay_order_info.id)
        if not ret:
            resp['code'] = -1
            resp['msg'] = '系统繁忙，稍后再试'
            return jsonify(resp)
    elif act == 'confirm':
        pay_order_info.express_status = 1
        db.session.commit()

    return jsonify(resp)


@api_bp.route('/member/info')
def member_info():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    member_obj = g.member_obj
    resp['data']['info'] = {
        'nickname': member_obj.nickname,
        'avatar_url': member_obj.avatar
    }
    return jsonify(resp)


@api_bp.route('/comment/list')
def comment_list():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    member_obj = g.member_obj
    c_list = MemberComments.query.filter_by(member_id=member_obj.id).order_by(-MemberComments.id).all()

    data_comment_list = []
    if c_list:
        pass

