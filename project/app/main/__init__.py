from flask import Blueprint

# 创建主页面模块蓝图
bp = Blueprint('main', __name__)

# 导入视图函数，确保路由被注册
from app.main import routes
