from flask_migrate import Migrate
from apps import create_app
from apps.utils.utils import ops_render, add_error_log
from config.exts import db
from apps.models.food_models import *
from apps.models.wx_models import *

app = create_app()


# 捕获404错误,添加错误记录
@app.errorhandler(404)
def error_404(err):
    add_error_log(str(err))
    return ops_render('error/error.html', {'status': 404, 'msg': '很抱歉,您访问的页面不存在'})


# 命令工具
migrate = Migrate(app=app, db=db)
