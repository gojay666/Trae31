from flask import Blueprint

# 创建认证模块蓝图
bp = Blueprint('auth', __name__)

# 导入视图函数，确保路由被注册
from app.auth import routes
