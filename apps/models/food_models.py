#!/usr/bin/env python3
# coding=utf-8
# Author:LGSP_Harold
from datetime import datetime

from apps.models import BaseModel
from config import constants
from config.exts import db


class User(BaseModel):
    # 用户表
    __tablename__ = 'user'

    nickname = db.Column(db.String(100), nullable=False, default='匿名', comment='昵称')
    mobile = db.Column(db.String(20), nullable=False, comment='手机号码')
    email = db.Column(db.String(100), nullable=False, comment='邮箱地址')
    sex = db.Column(db.SmallInteger, nullable=False, default=0, comment='1：男；2：女；0：未填写')
    avatar = db.Column(db.String(1024), comment='头像')
    login_name = db.Column(db.String(20), nullable=False, unique=True, comment='登录名')
    login_pwd = db.Column(db.String(128), nullable=False, comment='登陆密码')
    login_salt = db.Column(db.String(32), nullable=False, comment='登陆密码的随机加密密钥')
    status = db.Column(db.SmallInteger, nullable=False, default=1, comment='1：有效；0：无效')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='最后操作时间')


class AccessLog(BaseModel):
    # 用户访问记录表
    __tablename__ = 'access_log'

    uid = db.Column(db.Integer, nullable=False, default=0, comment='用户id')
    referer_url = db.Column(db.String(255), nullable=False, default='', comment='当前访问的refer')
    target_url = db.Column(db.String(255), nullable=False, default='', comment='访问的URL')
    query_params = db.Column(db.Text, nullable=False, default='', comment='请求参数')
    ua = db.Column(db.String(255), nullable=False, default='', comment='访问ua')
    ip = db.Column(db.String(32), nullable=False, default='', comment='访问IP')
    note = db.Column(db.String(1024), nullable=False, default='', comment='json格式备注字段')


class ErrorLog(BaseModel):
    # 错误日志表
    __tablename__ = 'error_log'

    uid = db.Column(db.Integer, comment='用户id')
    referer_url = db.Column(db.String(255), nullable=False, default='', comment='当前访问的refer')
    target_url = db.Column(db.String(255), nullable=False, default='', comment='访问的URL')
    query_params = db.Column(db.Text, nullable=False, default='', comment='请求参数')
    ua = db.Column(db.String(255), nullable=False, default='', comment='访问ua')
    ip = db.Column(db.String(32), nullable=False, default='', comment='访问IP')
    content = db.Column(db.Text, nullable=False, default='', comment='日志内容')


class Food(BaseModel):
    # 食物表
    __tablename__ = 'food'

    name = db.Column(db.String(100), nullable=False, comment='食物名称')
    price = db.Column(db.DECIMAL(10, 2), nullable=False, comment='售卖金额')
    main_image = db.Column(db.String(100), comment='主图')
    summary = db.Column(db.Text, nullable=False, comment='描述')
    stock = db.Column(db.Integer, nullable=False, comment='库存量')
    tags = db.Column(db.String(200), nullable=False, default='', comment='tag关键字，以”，“连接')
    status = db.Column(db.SmallInteger, nullable=False, default='1', comment='状态：1、有效，0、无效')
    month_count = db.Column(db.Integer, default='0', comment='月销售数量')
    total_count = db.Column(db.Integer, default='0', comment='总销售量')
    view_count = db.Column(db.Integer, default='0', comment='总浏览次数')
    comment_count = db.Column(db.Integer, default='0', comment='总评论量')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='最后更新时间')

    cat_id = db.Column(db.Integer, db.ForeignKey('food_cat.id'), nullable=False)
    cat = db.relationship('FoodCat', backref='food')


class FoodCat(BaseModel):
    # 食物分类表
    __tablename__ = 'food_cat'

    name = db.Column(db.String(100), nullable=False, comment='类别名称')
    weight = db.Column(db.SmallInteger, default=1, comment='权重')
    status = db.Column(db.SmallInteger, nullable=False, default='1', comment='状态：1、有效，0、无效')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='最后更新时间')

    @property
    def status_desc(self):
        return constants.STATUS_MAPPING[str(self.status)]


class FoodSaleChangeLog(BaseModel):
    # 食物销售情况表
    __tablename__ = 'food_sale_change_log'

    food_id = db.Column(db.Integer, nullable=False, comment='商品ID')
    quantity = db.Column(db.Integer, default=0, comment='售卖数量')
    price = db.Column(db.DECIMAL(10, 2), nullable=False, comment='售卖金额')
    member_id = db.Column(db.Integer, nullable=False, comment='用户ID')


class FoodStockChangeLog(BaseModel):
    # 库存数据变更表
    __tablename__ = 'food_stock_change_log'

    food_id = db.Column(db.Integer, nullable=False, comment='食物ID')
    unit = db.Column(db.Integer, default=0, comment='变更多少')
    total_stock = db.Column(db.Integer, nullable=False, comment='变更之后总量')
    note = db.Column(db.String(256), comment='备注字段')


class Files(BaseModel):
    # 文件上传记录表
    __tablename__ = 'files'

    file_key = db.Column(db.String(128), nullable=False, comment='文件名称')


class StatDailySite(BaseModel):
    # 全站日统计数据表
    __tablename__ = 'stat_daily_site'

    date = db.Column(db.DateTime, default=datetime.now, comment='日期')
    total_pay_monet = db.Column(db.DECIMAL(10, 2), comment='当日应收总金额')
    total_member_count = db.Column(db.Integer, default=0, comment='会员总数')
    total_new_member_count = db.Column(db.Integer,default=0,comment='当日新增会员数')
    total_order_count = db.Column(db.Integer,default=0, comment='当日订单数')
    total_shared_count = db.Column(db.Integer, default=0, comment='当日分享总数')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='最后更新时间')


class StatDailyMember(BaseModel):
    # 会员日统计数据表
    __tablename__ = 'stat_daily_member'

    date = db.Column(db.DateTime, default=datetime.now, comment='日期')
    member_id = db.Column(db.Integer, comment='会员ID')
    total_pay_money = db.Column(db.DECIMAL(10,2), comment='当日付款总金额')
    total_shared_count = db.Column(db.Integer, default=0, comment='当日分享总次数')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='最后更新时间')


class StatDailyFood(BaseModel):
    # 菜品日统计数据表
    __tablename__ = 'stat_daily_food'

    date = db.Column(db.DateTime, default=datetime.now, comment='日期')
    food_id = db.Column(db.Integer, comment='菜品ID')
    total_count = db.Column(db.Integer, default=0, comment='售卖总数量')
    total_pay_money = db.Column(db.DECIMAL(10,2), comment='总售卖金额')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='最后更新时间')
