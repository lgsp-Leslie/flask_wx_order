#!/usr/bin/env python3
# coding=utf-8
# Author:LGSP_Harold


# 格式化价格
def money_format(money):
    money = money
    if money % 2 == 0:
        money = int(money / 100)
    else:
        money = money / 100
    return money


# 格式化手机号
def mobile_format(mobile):
    mobile = str(mobile)
    mobile = mobile.replace(mobile[3:8], '****')
    return mobile


