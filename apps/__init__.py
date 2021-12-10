#!/usr/bin/env python3
# coding=utf-8
# Author:LGSP_Harold

from flask import Flask

from apps.api.view import api_bp
from apps.manage.views import manage_bp
from apps.utils.filter import money_format, mobile_format
from apps.utils.views import utils_bp
from apps.utils.views_api import utils_api_bp
from config import conf
from config.exts import cors, migrate

from apps.models import *


def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # 生产环境需修改成ProductionConfig
    app.config.from_object(conf.DevelopmentConfig)

    # 初始化SQLAlchemy
    db.init_app(app=app)
    # 初始化flask-migrate
    migrate.init_app(app, db)
    # 初始化跨域
    cors.init_app(app=app, supports_credentials=True)

    # 注册蓝图
    app.register_blueprint(utils_bp, url_prefix='/utils')
    app.register_blueprint(utils_api_bp, url_prefix='/utils_api')
    app.register_blueprint(manage_bp, url_prefix='/manage')
    app.register_blueprint(api_bp, url_prefix='/api')

    # 注册过滤器
    app.jinja_env.filters['money_format'] = money_format
    app.jinja_env.filters['mobile_format'] = mobile_format

    return app
