#!/usr/bin/env python3
# coding=utf-8
# Author:LGSP_Harold
import datetime
import json
import re
from decimal import Decimal

from flask import Blueprint, request, jsonify, make_response, redirect, url_for, g
from sqlalchemy import or_

from apps.models.food_models import User, AccessLog, FoodCat, Food, FoodStockChangeLog, StatDailySite
from apps.models.wx_models import Member
from apps.utils.utils import gene_pwd, gene_auth_code, ops_render, random_salt
from config import constants
from config.conf import Config
from config.exts import db

manage_bp = Blueprint('manage', __name__)


# 管理登录登录
@manage_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return ops_render('user/login.html')

    if request.method == 'POST':
        resp = {'code': 200, 'msg': '登录成功', 'data': {}}

        req = request.values
        login_name = req['login_name'] if 'login_name' in req else ''
        login_pwd = req['login_pwd'] if 'login_pwd' in req else ''

        if login_name is None or len(login_name) < 1:
            resp['code'] = -1
            resp['msg'] = '登录用户名不能为空'
            return jsonify(resp)

        if login_pwd is None or len(login_pwd) < 1:
            resp['code'] = -1
            resp['msg'] = '登录密码不能为空'
            return jsonify(resp)

        user_obj = User.query.filter_by(login_name=login_name).first()
        if not user_obj:
            resp['code'] = -1
            resp['msg'] = '请输入正确的用户名和密码'
            return jsonify(resp)

        if user_obj.login_pwd != gene_pwd(login_pwd, user_obj.login_salt):
            resp['code'] = -1
            resp['msg'] = '请输入正确的用户名和密码'
            return jsonify(resp)

        if user_obj.status != 1:
            resp['code'] = -1
            resp['msg'] = '账号已被禁用，请联系管理员处理！'
            return jsonify(resp)

        response = make_response(json.dumps(resp))

        _gene_auth_code = gene_auth_code(user_obj, 'user')
        if _gene_auth_code is None:
            resp['code'] = -1
            resp['msg'] = 'geneAuthCode不能为None！'
            return jsonify(resp)

        response.set_cookie(Config.AUTH_COOKIE_NAME, '%s#%s' % (_gene_auth_code, user_obj.id),
                            60 * 60 * 24 * 120)  # 保存120天

        return response


# 管理退出
@manage_bp.route('/logout')
def logout():
    response = make_response(redirect(url_for('manage.login')))
    response.delete_cookie(Config.AUTH_COOKIE_NAME)

    return response


# 管理首页
@manage_bp.route('/index')
def index():
    return ops_render('index/index.html')


# 管理编辑
@manage_bp.route('/user/edit', methods=['GET', 'PUT'])
def user_edit():
    if request.method == 'GET':
        return ops_render('user/edit.html', {'current': 'edit'})
    if request.method == 'PUT':
        resp = {'code': 200, 'msg': '修改成功', 'data': {}}

        req = request.values
        nickname = req['nickname'] if 'nickname' in req else ''
        email = req['email'] if 'email' in req else ''

        if nickname is None or len(nickname) < 1:
            resp['code'] = -1
            resp['msg'] = '昵称不能为空！'
            return jsonify(resp)

        if email is None or len(email) < 1:
            resp['code'] = -1
            resp['msg'] = 'Email不能为空!'
            return jsonify(resp)

        email_pattern = re.compile(r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$')
        if not email_pattern.match(email):
            resp['code'] = -1
            resp['msg'] = '请输入有效的Email地址！'
            return jsonify(resp)

        user_obj = g.current_user
        user_obj.nickname = nickname
        user_obj.email = email

        db.session.add(user_obj)
        db.session.commit()
        return resp


# 修改密码
@manage_bp.route('/user/reset/pwd', methods=['GET', 'PUT'])
def user_reset_pwd():
    if request.method == 'GET':
        return ops_render('user/reset_pwd.html', {'current': 'reset_pwd'})

    if request.method == 'PUT':
        resp = {'code': 200, 'msg': '密码修改成功，请重新登录！', 'data': {}}

        req = request.values

        old_pwd = req['old_pwd'] if 'old_pwd' in req else ''
        new_pwd = req['new_pwd'] if 'new_pwd' in req else ''
        re_new_pwd = req['re_new_pwd'] if 're_new_pwd' in req else ''

        if old_pwd is None or len(old_pwd) < 6:
            resp['code'] = -1
            resp['msg'] = '旧密码不能为空,且长度不能小于6！'
            return jsonify(resp)

        if new_pwd is None or len(new_pwd) < 6:
            resp['code'] = -1
            resp['msg'] = '新密码不能为空,且长度不能小于6！'
            return jsonify(resp)

        if re_new_pwd is None or len(re_new_pwd) < 6:
            resp['code'] = -1
            resp['msg'] = '确认新密码不能为空,且长度不能小于6！'
            return jsonify(resp)

        if re_new_pwd != new_pwd:
            resp['code'] = -1
            resp['msg'] = '两次输入的新密码不一致，请确认！'
            return jsonify(resp)

        if new_pwd == old_pwd:
            resp['code'] = -1
            resp['msg'] = '新密码和旧密码相同，请重新输入！'
            return jsonify(resp)

        user_obj = g.current_user
        old_pwd_str = gene_pwd(old_pwd, user_obj.login_salt)

        if user_obj.login_pwd != old_pwd_str:
            resp['code'] = -1
            resp['msg'] = '旧密码错误，请重新输入！'
            return jsonify(resp)

        login_salt = random_salt()
        user_obj.login_pwd = gene_pwd(new_pwd, login_salt)
        user_obj.login_salt = login_salt

        db.session.commit()

        # 如果想修改密码后不退出重新登录，替换下面这段代码
        # response = make_response(json.dumps(resp))
        # response.set_cookie(Config.AUTH_COOKIE_NAME, '%s#%s' % (gene_auth_code(user_obj, 'user'), user_obj.id), 60 * 60 * 24 * 120)  # 保存120天
        # return response

        return jsonify(resp)


# 用户列表
@manage_bp.route('/account/list')
def account_list():
    page = int(request.args.get('page', 1))

    query = User.query

    status_name = int(request.args.get('status', '-1'))
    if status_name > -1:
        query = query.filter(User.status == status_name)

    mix_kw = request.args.get('mix_kw', '')
    if mix_kw:
        rule = or_(User.nickname.contains('%s' % mix_kw), User.mobile.contains('%s' % mix_kw))
        page_data = query.filter(rule).order_by(User.id.desc()).paginate(page=page, per_page=Config.PER_PAGE)
    else:
        page_data = query.order_by(User.id.desc()).paginate(page=page, per_page=Config.PER_PAGE)

    resp_data = {
        'list': page_data,
        'status_mapping': constants.STATUS_MAPPING
    }

    return ops_render('account/index.html', resp_data)


# 用户详情
@manage_bp.route('/account/info')
def account_info():
    resp_data = {}
    u_id = int(request.args.get('id', 0))
    if u_id < 1:
        return redirect(url_for('manage.account_list'))

    user_obj = User.query.get(u_id)
    if not user_obj:
        return redirect(url_for('manage.account_list'))

    resp_data['info'] = user_obj

    access_obj = AccessLog.query.filter_by(uid=u_id).order_by(AccessLog.created_at.desc()).limit(5)

    if not access_obj:
        resp_data['access'] = None
    resp_data['access'] = access_obj

    return ops_render('account/info.html', resp_data)


# 账号新增、编辑
@manage_bp.route('/account/edit', methods=['GET', 'POST'])
def account_edit():
    if request.method == 'GET':
        u_id = int(request.args.get('id', 0))

        user_obj = None
        if u_id:
            user_obj = User.query.get(u_id)
        resp_data = {'info': user_obj}

        return ops_render('account/set.html', resp_data)

    if request.method == 'POST':
        resp = {'code': 200, 'msg': '修改成功！', 'data': {}}
        req = request.values
        u_id = req['id'] if 'id' in req else 0
        nickname = req['nickname'] if 'nickname' in req else ''
        mobile = req['mobile'] if 'mobile' in req else ''
        email = req['email'] if 'email' in req else ''
        login_name = req['login_name'] if 'login_name' in req else ''
        login_pwd = req['login_pwd'] if 'login_pwd' in req else ''

        if nickname is None or len(nickname) < 2:
            resp['code'] = -1
            resp['msg'] = '请输入符合规范的昵称!'
            return jsonify(resp)

        mobile_pattern = re.compile(r'^(13[0-9]|14[5|7]|15[0|1|2|3|4|5|6|7|8|9]|18[0|1|2|3|5|6|7|8|9])\d{8}$')
        if mobile is None or not mobile_pattern.match(mobile):
            resp['code'] = -1
            resp['msg'] = '请输入有效的手机号！'
            return jsonify(resp)

        if email is None or len(email) < 1:
            resp['code'] = -1
            resp['msg'] = 'Email不能为空!'
            return jsonify(resp)

        email_pattern = re.compile(r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$')

        if not email_pattern.match(email):
            resp['code'] = -1
            resp['msg'] = '请输入有效的Email地址！'
            return jsonify(resp)

        if login_name is None or len(login_name) < 2:
            resp['code'] = -1
            resp['msg'] = '请输入符合规范的用户名!'
            return jsonify(resp)

        if login_pwd is None or len(login_pwd) < 6:
            resp['code'] = -1
            resp['msg'] = '请输入符合规范的密码!'
            return jsonify(resp)

        has_user = User.query.filter(User.login_name == login_name, User.id != u_id).first()
        if has_user:
            resp['code'] = -1
            resp['msg'] = '该用户登录名已存在，请更换一个重新注册!'
            return jsonify(resp)

        user_obj = User.query.get(u_id)
        if not user_obj:
            resp['msg'] = '新增成功！'
            user_obj = User()

        user_obj.nickname = nickname
        user_obj.mobile = mobile
        user_obj.email = email
        user_obj.login_name = login_name
        login_salt = random_salt()
        user_obj.login_salt = login_salt
        user_obj.login_pwd = gene_pwd(login_pwd, login_salt)

        db.session.add(user_obj)
        db.session.commit()
        return jsonify(resp)


# 账户删除、恢复
@manage_bp.route('/account/ops', methods=['PUT'])
def account_ops():
    resp = {'code': 200, 'msg': '操作成功！', 'data': {}}
    req = request.values

    u_id = req['id'] if 'id' in req else 0
    act = req['act'] if 'act' in req else ''
    if not u_id:
        resp['code'] = -1
        resp['msg'] = '操作失败！'
        return jsonify(resp)
    if act not in ['remove', 'recover']:
        resp['code'] = -1
        resp['msg'] = '操作失败！'
        return jsonify(resp)
    user_obj = User.query.get(u_id)
    if not user_obj:
        resp['code'] = -1
        resp['msg'] = '指定账户不存在！'
        return jsonify(resp)
    if act == 'remove':
        user_obj.status = 0
    elif act == 'recover':
        user_obj.status = 1
    db.session.commit()
    return jsonify(resp)


# 食物列表
@manage_bp.route('/food/list')
def food_list():
    resp_data = {}

    page = int(request.args.get('page', 1))

    query = Food.query

    status_name = int(request.args.get('status', '-1'))
    if status_name > -1:
        query = query.filter(Food.status == status_name)

    cat_id = int(request.args.get('cat_id', 0))
    if cat_id > 0:
        query = query.filter_by(cat_id=cat_id)

    mix_kw = request.args.get('mix_kw', '')
    if mix_kw:
        rule = or_(Food.name.contains('%s' % mix_kw), Food.tags.contains('%s' % mix_kw))
        page_data = query.filter(rule).order_by(Food.id.desc()).paginate(page=page, per_page=Config.PER_PAGE)
    else:
        page_data = query.order_by(Food.id.desc()).paginate(page=page, per_page=Config.PER_PAGE)

    resp_data = {
        'list': page_data,
        'status_mapping': constants.STATUS_MAPPING
    }

    food_list_obj = FoodCat.query.all()
    resp_data['current'] = 'index'
    resp_data['cat_list'] = food_list_obj
    return ops_render('food/index.html', resp_data)


# 食物添加、编辑
@manage_bp.route('/food/edit', methods=['GET', 'POST'])
def food_edit():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    if request.method == 'GET':

        resp_data = {}
        req = request.args
        f_id = int(req.get('id', 0))

        food_obj = None
        if f_id:
            food_obj = Food.query.get(f_id)

        cat_list = FoodCat.query.all()
        resp_data['info'] = food_obj
        resp_data['current'] = 'index'
        resp_data['cat_list'] = cat_list

        return ops_render('food/set.html', resp_data)

    if request.method == 'POST':
        req = request.values

        f_id = req['food_id'] if 'food_id' in req else 0
        c_id = int(req['cat_id']) if 'cat_id' in req else 0
        name = req['name'] if 'name' in req else ''
        price = req['price'] if 'price' in req else ''
        main_image = req['main_image'] if 'main_image' in req else ''
        summary = req['summary'] if 'summary' in req else ''
        stock = int(req['stock']) if 'stock' in req else ''
        tags = req['tags'] if 'tags' in req else ''

        price = Decimal(price).quantize(Decimal('0.00'))

        # if f_id < 1:
        #     resp['code'] = -1
        #     resp['msg'] = '商品不存在！'
        #     return jsonify(resp)

        if c_id < 1:
            resp['code'] = -1
            resp['msg'] = '请选择分类'
            return jsonify(resp)

        if len(name) < 1 or name is None:
            resp['code'] = -1
            resp['msg'] = '名称不符合规范'
            return jsonify(resp)

        if price < 0 or price is None:
            resp['code'] = -1
            resp['msg'] = '售卖价格不能为空且大于等于0'
            return jsonify(resp)

        if main_image is None or len(main_image) < 3:
            resp['code'] = -1
            resp['msg'] = '请上传封面图'
            return jsonify(resp)

        if summary is None or len(summary) < 10:
            resp['code'] = -1
            resp['msg'] = '详情不能少于十个字符！'
            return jsonify(resp)

        if stock < 1:
            resp['code'] = -1
            resp['msg'] = '库存不能小于1'
            return jsonify(resp)

        if tags is None or len(tags) < 1:
            resp['code'] = -1
            resp['msg'] = '请输入标签！'
            return jsonify(resp)

        food_obj = Food.query.get(f_id)
        before_stock = 0

        if not food_obj:
            food_obj = Food()
        else:
            before_stock = food_obj.stock

        food_obj.cat_id = c_id
        food_obj.name = name
        food_obj.price = price
        food_obj.main_image = main_image
        food_obj.summary = summary
        food_obj.stock = stock
        food_obj.tags = tags

        db.session.add(food_obj)
        db.session.commit()

        stock_change = FoodStockChangeLog()
        stock_change.food_id = food_obj.id
        stock_change.unit = int(stock) - int(before_stock)
        stock_change.total_stock = stock
        stock_change.note = '后台调整'
        db.session.add(stock_change)
        db.session.commit()

        return jsonify(resp)


# 食物详情
@manage_bp.route('/food/info')
def food_info():
    resp_data = {}

    req = request.args
    f_id = int(req.get('id', 0))
    if f_id < 1:
        return redirect('manage.food_list')

    food_obj = Food.query.get(f_id)
    if not food_obj:
        return redirect('manage.food_list')

    stock_change_list = FoodStockChangeLog.query.filter(FoodStockChangeLog.food_id == f_id).order_by(
        FoodStockChangeLog.id.desc()).all()

    resp_data['info'] = food_obj
    resp_data['current'] = 'index'
    resp_data['stock_change_list'] = stock_change_list

    return ops_render('food/info.html', resp_data)


# 食物删除、恢复
@manage_bp.route('/food/ops', methods=['PUT'])
def foot_ops():
    resp = {'code': 200, 'msg': '操作成功！', 'data': {}}
    req = request.values

    f_id = req['id'] if 'id' in req else 0
    act = req['act'] if 'act' in req else ''
    if not f_id:
        resp['code'] = -1
        resp['msg'] = '操作失败！'
        return jsonify(resp)
    if act not in ['remove', 'recover']:
        resp['code'] = -1
        resp['msg'] = '操作失败！'
        return jsonify(resp)
    food_obj = Food.query.get(f_id)
    if not food_obj:
        resp['code'] = -1
        resp['msg'] = '指定食物不存在！'
        return jsonify(resp)
    if act == 'remove':
        food_obj.status = 0
    elif act == 'recover':
        food_obj.status = 1
    db.session.commit()
    return jsonify(resp)


# 食物类别列表
@manage_bp.route('/food/cat/list')
def food_cat_list():
    page = int(request.args.get('page', 1))
    query = FoodCat.query

    status_name = int(request.args.get('status', '-1'))
    if status_name > -1:
        query = query.filter(FoodCat.status == status_name)

    page_data = query.order_by(-FoodCat.weight, -FoodCat.id).paginate(page=page, per_page=Config.PER_PAGE)

    resp_data = {
        'list': page_data,
        'status_mapping': constants.STATUS_MAPPING,
        'current': 'cat'
    }

    return ops_render('food/cat.html', resp_data)


# 食物类别编辑、添加
@manage_bp.route('/food/cat/edit', methods=['GET', 'POST'])
def food_cat_edit():
    if request.method == 'GET':
        resp_data = {}
        req = request.args
        c_id = int(req.get('id', 0))
        info = None
        if c_id:
            info = FoodCat.query.get(c_id)
        resp_data['info'] = info
        resp_data['current'] = 'cat'

        return ops_render('food/cat_set.html', resp_data)

    if request.method == 'POST':
        resp = {'code': 200, 'msg': '操作成功！', 'data': {}}
        req = request.values

        c_id = req['id'] if 'id' in req else 0
        name = req['name'] if 'name' in req else ''
        weight = int(req['weight']) if ('weight' in req and int(req['weight']) > 0) else 1

        if not name or len(name) < 1:
            resp['code'] = -1
            resp['msg'] = '类别名称不能为空！'
            return jsonify(resp)

        info = FoodCat.query.get(c_id)
        if not info:
            info = FoodCat()

        info.name = name
        info.weight = weight
        db.session.add(info)
        db.session.commit()
        return jsonify(resp)


# 食物类别删除、恢复
@manage_bp.route('/food/cat/ops', methods=['PUT'])
def foot_cat_ops():
    resp = {'code': 200, 'msg': '操作成功！', 'data': {}}
    req = request.values

    c_id = req['id'] if 'id' in req else 0
    act = req['act'] if 'act' in req else ''
    if not c_id:
        resp['code'] = -1
        resp['msg'] = '操作失败！'
        return jsonify(resp)
    if act not in ['remove', 'recover']:
        resp['code'] = -1
        resp['msg'] = '操作失败！'
        return jsonify(resp)
    cat_obj = FoodCat.query.get(c_id)
    if not cat_obj:
        resp['code'] = -1
        resp['msg'] = '指定类别不存在！'
        return jsonify(resp)
    if act == 'remove':
        cat_obj.status = 0
    elif act == 'recover':
        cat_obj.status = 1
    db.session.commit()
    return jsonify(resp)


# 用户列表
@manage_bp.route('/member/list')
def member_list():
    resp_data = {}
    page = int(request.args.get('page', 1))
    query = Member.query

    status_name = int(request.args.get('status', '-1'))
    if status_name > -1:
        query = query.filter(Member.status == status_name)

    mix_kw = request.args.get('mix_kw', '')
    if mix_kw:
        rule = or_(Member.nickname.contains('%s' % mix_kw), Member.mobile.contains('%s' % mix_kw))
        page_data = query.filter(rule).order_by(Member.id.desc()).paginate(page=page, per_page=Config.PER_PAGE)
    else:
        page_data = query.order_by(Member.id.desc()).paginate(page=page, per_page=Config.PER_PAGE)

    resp_data['list'] = page_data
    resp_data['current'] = 'index'
    resp_data['status_mapping'] = constants.STATUS_MAPPING
    return ops_render('member/index.html', resp_data)


# 用户详情
@manage_bp.route('/member/info')
def member_info():
    resp_data = {}
    req = request.args
    m_id = int(req.get('id', 0))
    if m_id < 1:
        return redirect(url_for('manage.member_list'))

    info = Member.query.get(m_id)
    if not info:
        return redirect(url_for('manage.member_list'))

    resp_data['info'] = info
    resp_data['current'] = 'index'

    return ops_render('member/info.html', resp_data)


# 账户编辑
@manage_bp.route('/member/edit', methods=['GET', 'PUT'])
def member_edit():
    if request.method == 'GET':
        resp_data = {}
        req = request.args
        m_id = int(req.get('id', 0))
        if m_id < 1:
            return redirect(url_for('manage.member_list'))

        info = Member.query.get(m_id)
        if not info:
            return redirect(url_for('manage.member_list'))
        if info.status != 1:
            return redirect(url_for('manage.member_list'))

        resp_data['info'] = info

        return ops_render('member/set.html', resp_data)

    if request.method == 'PUT':
        resp = {'code': 200, 'msg': '修改成功！', 'data': {}}
        req = request.values
        nickname = req['nickname'] if 'nickname' in req else ''
        if nickname is None or len(nickname) < 1:
            resp['code'] = -1
            resp['msg'] = '请输入符合规范的昵称！'
            return jsonify(resp)

        m_id = req['id'] if 'id' in req else 0
        if m_id is None or len(m_id) < 1:
            resp['code'] = -1
            resp['msg'] = '用户ID不不能为空'
            return jsonify(resp)

        info = Member.query.get(m_id)
        if not info:
            resp['code'] = -1
            resp['msg'] = '用户不存在'
            return jsonify(resp)

        info.nickname = nickname
        db.session.commit()
        return jsonify(resp)


# 账户删除、恢复
@manage_bp.route('/member/ops', methods=['PUT'])
def member_ops():
    resp = {'code': 200, 'msg': '操作成功！', 'data': {}}
    req = request.values

    m_id = req['id'] if 'id' in req else 0
    act = req['act'] if 'act' in req else ''
    if not m_id:
        resp['code'] = -1
        resp['msg'] = '操作失败！'
        return jsonify(resp)
    if act not in ['remove', 'recover']:
        resp['code'] = -1
        resp['msg'] = '操作失败！'
        return jsonify(resp)
    member_obj = Member.query.get(m_id)
    if not member_obj:
        resp['code'] = -1
        resp['msg'] = '指定用户不存在！'
        return jsonify(resp)
    if act == 'remove':
        member_obj.status = 0
    elif act == 'recover':
        member_obj.status = 1
    db.session.commit()
    return jsonify(resp)


@manage_bp.route('/member/comment')
def member_comment():
    return ops_render('member/comment.html')


@manage_bp.route('/finance/list')
def finance_list():
    return ops_render('finance/index.html')


@manage_bp.route('/finance/account/list')
def finance_account_list():
    return ops_render('finance/account.html')


@manage_bp.route('/finance_pay_info')
def finance_pay_info():
    return ops_render('finance/pay_info.html')


@manage_bp.route('/stat/list')
def stat_list():
    return ops_render('stat/index.html')


@manage_bp.route('/stat/member')
def stat_member():
    return ops_render('stat/member.html')


@manage_bp.route('/stat/food')
def stat_food():
    return ops_render('stat/food.html')


@manage_bp.route('/stat/share')
def stat_share():
    return ops_render('stat/share.html')


@manage_bp.route('/chart/dashboard')
def chart_dashboard():
    date_before_30day = datetime.datetime.now() + datetime.timedelta(days=-30)
    date_from = date_before_30day.strftime('%Y-%m-%d')
    date_to = datetime.datetime.now().strftime('%Y-%m-%d')

    _list = StatDailySite.query.filter(StatDailySite.date >= date_from, StatDailySite.date <= date_to).order_by(
        StatDailySite.id.asc()).all()

    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    data = {
        'categories': [],
        'series': [
            {
                'name': '会员总数',
                'data': []
            },
            {
                'name': '订单总数',
                'data': []
            }
        ]
    }
    if _list:
        for item in _list:
            data['categories'].append(item.date.strftime('%Y-%m-%d'))
            data['series'][0]['data'].append(item.total_member_count)
            data['series'][1]['data'].append(item.total_order_count)
    resp['data'] = data
    return jsonify(resp)


@manage_bp.route('/chart/finance')
def chart_finance():
    date_before_30day = datetime.datetime.now() + datetime.timedelta(days=-30)
    date_from = date_before_30day.strftime('%Y-%m-%d')
    date_to = datetime.datetime.now().strftime('%Y-%m-%d')

    _list = StatDailySite.query.filter(StatDailySite.date >= date_from, StatDailySite.date <= date_to).order_by(
        StatDailySite.id.asc()).all()

    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    data = {
        'categories': [],
        'series': [
            {
                'name': '日营收情况',
                'data': []
            }
        ]
    }
    if _list:
        for item in _list:
            data['categories'].append(item.date.strftime('%Y-%m-%d'))
            data['series'][0]['data'].append(float(item.total_pay_money))
    resp['data'] = data
    return jsonify(resp)
