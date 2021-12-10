#!/usr/bin/env python3
# coding=utf-8
# Version:python3.6.1
# File:views.py
# Author:LGSP_Harold
import json
import os
import re
from flask import Blueprint, request, current_app, redirect, url_for, g, jsonify
from apps.utils.utils import add_access_log, upload_image, check_login, list_image, upload_file
from config.conf import Config

utils_bp = Blueprint('utils', __name__)


# 钩子函数,检查是否登录账号，用于验证后台管理
@utils_bp.before_app_request
def before_request():
    # 未登录拦截
    ignore_urls = Config.IGNORE_URLS
    ignore_check_login_urls = Config.IGNORE_CHECK_LOGIN_URLS
    path = request.path

    pattern = re.compile('%s' % '|'.join(ignore_check_login_urls))
    if pattern.match(path):
        return

    user_obj = check_login()

    g.current_user = None
    if user_obj:
        g.current_user = user_obj

    # 加入访问日志
    add_access_log()

    pattern = re.compile('%s' % '|'.join(ignore_urls))
    if pattern.match(path):
        return

    if not user_obj:
        return redirect(url_for('manage.login'))
    return


# 富文本图片上传
@utils_bp.route('/ueditor/upload', methods=['GET', 'POST'])
def ueditor_upload():
    req = request.values
    action = req['action'] if 'action' in req else ''

    if action == 'config':
        with open(os.path.join(current_app.static_folder, 'plugins', 'ueditor', 'upload_config.json')) as fp:
            try:
                config_data = json.loads(re.sub(r'\/\*.*\*\/', '', fp.read()))
            except:
                config_data = {}
        return jsonify(config_data)

    if action == 'uploadimage':
        return upload_image()

    if action == 'listimage':
        return list_image()

    return 'upload'


# 图片上传
@utils_bp.route('/upload_pic', methods=['GET', 'POST'])
def upload_pic():
    file_target = request.files
    upfile = file_target['upfile'] if 'upfile' in file_target else None

    callback_target = 'window.parent'

    if upfile is None:
        return '<script>{0}.error("{1}")</script>'.format(callback_target, '上传失败')

    ret = upload_file(upfile)
    if ret['code'] != 200:
        return '<script>{0}.error("{1}")</script>'.format(callback_target, '上传失败:' + ret['msg'])

    return '<script>{0}.success("{1}")</script>'.format(callback_target, ret['data']['file_key'])
