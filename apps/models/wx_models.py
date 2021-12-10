#!/usr/bin/env python3
# coding=utf-8
# Author:LGSP_Harold
from datetime import datetime

from apps.models import BaseModel
from config import constants
from config.exts import db


class Member(BaseModel):
    # 会员表
    __tablename__ = 'member'

    nickname = db.Column(db.String(100), nullable=False, default='匿名', comment='昵称')
    mobile = db.Column(db.String(20), comment='手机号码')
    sex = db.Column(db.SmallInteger, nullable=False, default=0, comment='1：男；2：女；0：未填写')
    avatar = db.Column(db.String(1024), comment='头像')
    login_salt = db.Column(db.String(32), nullable=False, comment='随机加密密钥')
    reg_ip = db.Column(db.String(32), comment='注册IP')
    status = db.Column(db.SmallInteger, nullable=False, default=1, comment='1：有效；0：无效')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='最后更新时间')

    @property
    def status_desc(self):
        return constants.STATUS_MAPPING[str(self.status)]

    @property
    def sex_desc(self):
        sex_mapping = {
            '0': '未知',
            '1': '男',
            '2': '女'
        }
        return sex_mapping[str(self.sex)]


class OauthMemberBind(BaseModel):
    # 第三方登录绑定关系表
    __tablename__ = 'oauth_member_bind'

    member_id = db.Column(db.Integer, nullable=False, comment='会员ID')
    client_type = db.Column(db.String(32), comment='客户端来源')
    type = db.Column(db.String(32), comment='账号来源')
    openid = db.Column(db.String(128), nullable=False, default='', comment='第三方ID')
    unionid = db.Column(db.String(128), comment='用户在开放平台的唯一标识符')
    extra = db.Column(db.Text, comment='额外字段')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='最后更新时间')


class MemberCart(BaseModel):
    # 购物车表
    __tablename__ = 'member_cart'

    member_id = db.Column(db.Integer, nullable=False, comment='会员ID')
    quantity = db.Column(db.Integer, nullable=False, comment='数量')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='最后更新时间')

    food_id = db.Column(db.Integer, db.ForeignKey('food.id'))
    food = db.relationship('Food', backref='member_cart')


class ShareHistory(BaseModel):
    # 分享记录数据表
    __tablename__ = 'share_history'

    member_id = db.Column(db.Integer, nullable=False, comment='会员ID')
    share_url = db.Column(db.String(256), nullable=False, comment='分享页面URL')
    device = db.Column(db.String(64), comment='分享应用或设备')


class PayOrder(BaseModel):
    # 订单数据表
    __tablename__ = 'pay_order'

    order_sn = db.Column(db.String(128), nullable=False, comment='随机订单号')
    member_id = db.Column(db.Integer, nullable=False, comment='会员ID')
    total_price = db.Column(db.DECIMAL(10, 2), nullable=False, comment='订单应付金额')
    freight_price = db.Column(db.DECIMAL(10, 2), default=0.00, comment='运费')
    pay_price = db.Column(db.DECIMAL(10, 2), nullable=False, comment='订单实付金额')
    pay_sn = db.Column(db.String(128), comment='第三方流水号')
    prepay_id = db.Column(db.String(128), comment='第三方预付id')
    note = db.Column(db.Text, comment='备注')
    status = db.Column(db.SmallInteger, default=0, comment='1：支付完成、0：无效、-1：申请退款、-2：退款中、-9：退款成功、-8：待支付、-7：完成支付待确认')
    express_status = db.Column(db.SmallInteger, default=0, comment='1：确认收货、0：失败、-8：待支付、-7：已付款待发货')
    express_address_id = db.Column(db.String(128), comment='快递地址ID')
    express_info = db.Column(db.Text, comment='快递信息')
    comment_status = db.Column(db.SmallInteger, default=0, comment='评论状态')
    order_time = db.Column(db.DateTime, default=datetime.now, comment='下单时间')
    pay_time = db.Column(db.DateTime, default=datetime.now, comment='付款时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='最后更新时间')

    @property
    def pay_status(self):
        tmp_status = self.status
        if self.status == 1:
            tmp_status = self.express_status
            if self.express_status == 1 and self.comment_status == 0:
                tmp_status = -5
            if self.express_status == 1 and self.comment_status == 1:
                tmp_status = 1
        return tmp_status

    @property
    def status_desc(self):
        return constants.PAY_STATUS_DISPLAY_MAPPING[str(self.status)]

    @property
    def order_number(self):
        order_number = self.created_at.strftime('%Y%m%d%H%M%S')
        order_number = order_number + str(self.id).zfill(5)
        return order_number


class PayOrderItem(BaseModel):
    # 订单商品数据表
    __tablename__ = 'pay_order_item'

    pay_order_id = db.Column(db.Integer, nullable=False, comment='订单ID')
    member_id = db.Column(db.Integer, nullable=False, comment='会员ID')
    quantity = db.Column(db.Integer, nullable=False, comment='商品购买数量')
    price = db.Column(db.DECIMAL(10, 2), nullable=False, comment='商品总价格，售价*数量')
    food_id = db.Column(db.Integer, nullable=False, comment='商品ID')
    note = db.Column(db.Text, comment='备注')
    status = db.Column(db.SmallInteger, default=1, comment='状态：1成功、0失败')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='最后更新时间')


class PayOrderCallbackData(BaseModel):
    # 支付回调数据表
    __tablename__ = 'pay_order_callback_data'

    pay_order_id = db.Column(db.Integer, nullable=False, comment='支付订单ID')
    pay_data = db.Column(db.Text, comment='支付回调信息')
    refund_data = db.Column(db.Text, comment='退款回调信息')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='最后更新时间')


class QueueList(BaseModel):
    # 事件队列表
    __tablename__ = 'queue_list'

    queue_name = db.Column(db.String(30), nullable=False, comment='队列名字')
    data = db.Column(db.String(1024), nullable=False, comment='队列数据')
    status = db.Column(db.SmallInteger, default=-1, comment='状态：-1、待处理；1、已处理。')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='最后更新时间')


class OauthAccessToken(BaseModel):
    # 调用Token时效表
    __tablename__ = 'oauth_access_token'

    access_token = db.Column(db.String(600), nullable=False, comment='access_token')
    expired_at = db.Column(db.DateTime, comment='过期时间')


class MemberComments(BaseModel):
    # 会员评论表
    __tablename__ = 'member_comments'

    member_id = db.Column(db.Integer, nullable=False, comment='会员ID')
    foods_ids = db.Column(db.String(256), comment='商品ID')
    pay_order_id = db.Column(db.Integer, nullable=False, comment='订单ID')
    score = db.Column(db.SmallInteger, default=0, comment='评分')
    content = db.Column(db.Text, nullable=False, comment='评论内容')

