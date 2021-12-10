#!/usr/bin/env python3
# coding=utf-8
# Author:LGSP_Harold
from apps.models.food_models import Food, FoodStockChangeLog
from apps.models.wx_models import PayOrder, PayOrderItem
from config.exts import db


def close_order(pay_order_id=0):
    if pay_order_id < 1:
        return False
    pay_order_info = PayOrder.query.filter_by(id=pay_order_id, status=-8).first()
    if not pay_order_info:
        return False

    pay_order_items = PayOrderItem.query.filter_by(pay_order_id=pay_order_id).all()
    if pay_order_items:
        for item in pay_order_items:
            tmp_food_info = Food.query.get(item.food_id)
            if tmp_food_info:
                tmp_food_info.stock = tmp_food_info.stock + item.quantity

                model_stock_change = FoodStockChangeLog()
                model_stock_change.food_id = item.food_id
                model_stock_change.unit = item.quantity
                model_stock_change.total_stock = tmp_food_info.stock
                model_stock_change.note = '订单取消'
                db.session.add(model_stock_change)

    pay_order_info.status = 0
    db.session.commit()
