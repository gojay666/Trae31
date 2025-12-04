from flask import Blueprint

# 创建业务管理模块蓝图
bp = Blueprint('business', __name__)

# 导入视图函数，确保路由被注册
from app.business import routes
