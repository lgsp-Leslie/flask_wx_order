#!/usr/bin/env python3
# coding=utf-8
# Author:LGSP_Harold
import json
from datetime import datetime, timedelta

import requests
from flask import current_app
# from sqlalchemy import func

from apps.models.food_models import Food, FoodSaleChangeLog
from apps.models.wx_models import QueueList, PayOrder, PayOrderItem, OauthMemberBind, OauthAccessToken
# from apps.utils.utils import get_access_token
from config.conf import Config
from config.exts import db


class QueueService:
    @staticmethod
    def add_queue(queue_name, data=None):
        model_queue = QueueList()
        model_queue.queue_name = queue_name

        if data:
            model_queue.data = json.dumps(data)

        db.session.add(model_queue)
        db.session.commit()
        return True

    def run(self, params):
        _list = QueueList.query.filter_by(status=-1).order_by(QueueList.id.asc()).limit(1).all()

        for item in _list:
            if item.queue_name == 'pay':
                self.handle_pay(item)

            item.status = 1
            db.session.commit()

    def handle_pay(self, item):
        data = json.loads(item.data)
        if 'member_id' not in data or 'pay_order_id' not in data:
            return False
        pay_order_info = PayOrder.query.filter_by(id=data['pay_order_id']).first()
        if not pay_order_info:
            return False

        pay_order_items = PayOrderItem.query.filter_by(pay_order_id=pay_order_info.id).all()
        notice_content = []
        if pay_order_items:
            for item in pay_order_items:
                tmp_food_info = Food.query.get(item.food_id)
                if not tmp_food_info:
                    continue

                notice_content.append('%s %s份' % (tmp_food_info.name, item.quantity))

                # 更新销售数量
                date_from = datetime.now().strftime('%Y-%m-01 00:00:00')
                date_to = datetime.now().strftime('%Y-%m-31 23:59:59')

                # 当月销量
                tmp_stat_info = db.session.query(FoodSaleChangeLog,
                                                 db.func.sum(FoodSaleChangeLog.quantity).label('total')).filter(
                    FoodSaleChangeLog.food_id == item.food_id, FoodSaleChangeLog.created_at >= date_from,
                    FoodSaleChangeLog.created_at <= date_to).first()

                tmp_mouth_count = tmp_stat_info[1] if tmp_stat_info[1] else 0

                tmp_food_info.total_count += 1
                tmp_food_info.month_count = tmp_mouth_count

                db.session.commit()

        keyword1_val = pay_order_info.note if pay_order_info.note else '无'
        keyword2_val = '、'.join(notice_content)
        keyword3_val = str(pay_order_info.total_price)
        keyword4_val = str(pay_order_info.order_number)
        keyword5_val = ''

        access_token = self.get_access_token()

        headers = {
            'Content-Type': 'application/json'
        }

        url = 'https://api.weixin.qq.com/cgi-bin/message/wxopen/template/uniform_send?access_token=%s' % access_token

        oauth_bind_info = OauthMemberBind.query.filter_by(member_id=data['member_id']).first()
        if not oauth_bind_info:
            return False

        params = {
            "touser": oauth_bind_info.openid,
            "mp_template_msg": {
                "appid": Config.WX_APPID,
                "template_id": Config.WX_TEMPLATE,
                "url": Config.DOMAIN,
                "miniprogram": {
                    "appid": Config.WX_APPID,
                    "pagepath": "pages/my/order_list"
                },
                "data": {
                    "first": {
                        "value": "恭喜你购买成功！",
                        "color": "#173177"
                    },
                    "keyword1": {
                        "value": keyword2_val,
                        "color": "#173177"
                    },
                    "keyword2": {
                        "value": keyword3_val,
                        "color": "#173177"
                    },
                    "keyword3": {
                        "value": keyword4_val,
                        "color": "#173177"
                    },
                    "remark": {
                        "value": keyword1_val,
                        "color": "#173177"
                    }
                }
            }
        }

        r = requests.post(url=url, data=json.dumps(params), headers=headers)
        r.encoding = 'utf-8'
        current_app.logger.info(r.text)

        return True

    # 获取微信access token
    def get_access_token(self):
        token = None

        token_info = OauthAccessToken.query.filter(OauthAccessToken.expired_at > datetime.now()).first()
        if token_info:
            token = token_info.access_token
            return token

        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}'.format(
            Config.WX_APPID, Config.WX_SECRET)

        r = requests.get(url=url)
        if r.status_code != 200:
            return token

        data = json.loads(r.text)
        date = datetime.now() + timedelta(seconds=data['expires_in'] - 200)
        model_token = OauthAccessToken()
        model_token.access_token = data['access_token']
        model_token.expired_at = date.strftime('%Y-%m-%d %H:%M:%S')
        db.session.add(model_token)
        db.session.commit()

        return data['access_token']
