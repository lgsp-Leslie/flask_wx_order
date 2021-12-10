#!/usr/bin/env python3
# coding=utf-8
# Version:python3.6.1
# File:views.py
# Author:LGSP_Harold
import json
import os
import re
from flask import Blueprint, request, redirect, url_for, g, jsonify

from apps.utils.utils import check_member_login
from config.conf import Config

utils_api_bp = Blueprint('utils_api', __name__)


# 钩子函数,检查是否登录账号，用于验证后台管理
@utils_api_bp.before_app_request
def before_request():
    # 未登录拦截
    api_ignore_urls = Config.API_IGNORE_URLS
    path = request.path

    # 钩子函数，用于检测API请求，检测微信当前用户
    if '/api' not in path:
        return

    member_obj = check_member_login()

    g.member_obj = None
    if member_obj:
        g.member_obj = member_obj

    pattern = re.compile('%s' % '|'.join(api_ignore_urls))
    if pattern.match(path):
        return

    if not member_obj:
        resp = {'code': -1, 'msg': '未授权登录！', 'data': {}}
        return jsonify(resp)

    return

