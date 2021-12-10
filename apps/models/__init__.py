#!/usr/bin/env python3
# coding=utf-8
# Author:LGSP_Harold
from datetime import datetime
from config.exts import db


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='表id')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
