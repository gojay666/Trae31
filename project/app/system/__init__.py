from flask import Blueprint

# 创建系统设置模块蓝图
bp = Blueprint('system', __name__)

# 导入视图函数，确保路由被注册
from app.system import routes
