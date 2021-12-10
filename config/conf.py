#!/usr/bin/env python3
# coding=utf-8
# Author:LGSP_Harold
import datetime
import os

from config.db_mysql import Mysql
from config.secret import Secret
from config.wx_conf import WXConfig


class Config:
    # MySql配置
    SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@{}:{}/{}?charset={}' \
        .format(Mysql.DATABASE_USER,
                Mysql.DATABASE_PWD, Mysql.HOSTNAME,
                Mysql.PORT, Mysql.DATABASE,
                Mysql.DATABASE_CHARSET)

    DEBUG = True
    # SQLALCHEMY配置
    # 记录打印SQL语句
    SQLALCHEMY_ECHO = True
    # 数据库连接池的大小
    SQLALCHEMY_POOL_SIZE = 5
    # 数据库连接池超时时间
    SQLALCHEMY_POOL_TIMEOUT = 9
    # 自动回收连接的秒数。这对MySQL是必须的，默认情况下MySQL会自动移除闲置8小时或者以上的连接,Flask-SQLAlchemy会自动地设置这个值为 2 小时。也就是说如果连接池中有连接2个小时被闲置，那么其会被断开和抛弃；
    SQLALCHEMY_POOL_RECYCLE = 9
    # 控制在连接池达到最大值后可以创建的连接数。当这些额外的连接使用后回收到连接池后将会被断开和抛弃。保证连接池只有设置的大小；
    SQLALCHEMY_MAX_OVERFLOW = 5
    # 如果设置成 True (默认情况)，Flask-SQLAlchemy 将会追踪对象的修改并且发送信号。这需要额外的内存，如果不必要的可以禁用它。
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    SECRET_KEY = Secret.SECRET_KEY
    AUTH_COOKIE_NAME = "lgsp_food"

    # 设置全局session失效时间
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=30)

    # 项目根路径
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    # 静态文件夹路径
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    # 模板文件夹路径
    TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

    # 域名
    DOMAIN = 'http://127.0.0.1:5001'

    # 文件上传配置
    UPLOAD = {
        'ext': ['jpg', 'gif', 'bmp', 'jpeg', 'png'],
        'prefix_path': 'static/upload/',
        'prefix_url': 'static/upload/'
    }

    # 分页数据量
    PER_PAGE = 4

    # 不需验证的url
    IGNORE_URLS = [
        '^/manage/login',
        '^/api'
    ]
    IGNORE_CHECK_LOGIN_URLS = [
        '^/static',
        '^/favicon.ico'
    ]

    API_IGNORE_URLS = [
        '^/api'
    ]

    # 微信小程序配置
    WX_APPID = WXConfig.APPID
    WX_SECRET = WXConfig.SECRET
    WX_PAYKEY = WXConfig.PAYKEY
    WX_MCH_ID = WXConfig.MCH_ID
    WX_CALLBACK_URL = WXConfig.CALLBACK_URL
    WX_TEMPLATE = WXConfig.TEMPLATE_ID


class DevelopmentConfig(Config):
    ENV = 'deployment'
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_POOL_SIZE = 18
    SQLALCHEMY_POOL_TIMEOUT = 60
    SQLALCHEMY_POOL_RECYCLE = 18
    SQLALCHEMY_MAX_OVERFLOW = 9
    SQLALCHEMY_TRACK_MODIFICATIONS = False
