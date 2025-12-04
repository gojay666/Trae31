from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建数据库实例
db = SQLAlchemy()
# 创建迁移实例
migrate = Migrate()
# 创建登录管理器实例
login_manager = LoginManager()
# 设置登录视图
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


def create_app(config_class=None):
    """创建Flask应用实例"""
    import os
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    app = Flask(__name__, 
                template_folder=os.path.join(basedir, 'templates'),
                static_folder=os.path.join(basedir, 'static'))
    
    # 配置应用
    if config_class is None:
        app.config.from_prefixed_env()
    else:
        app.config.from_object(config_class)
    
    # 设置SECRET_KEY
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 导入datetime模块并添加到Jinja2环境
    import datetime
    app.jinja_env.globals['datetime'] = datetime
    app.jinja_env.globals['now'] = datetime.datetime.now
    
    # 设置SQLite数据库连接
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 确保上传目录存在
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'static/uploads'), exist_ok=True)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # 注册蓝图
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.business import bp as business_bp
    app.register_blueprint(business_bp, url_prefix='/business')
    
    from app.system import bp as system_bp
    app.register_blueprint(system_bp, url_prefix='/system')
    
    from app.crawler import bp as crawler_bp
    app.register_blueprint(crawler_bp)
    
    return app


from app import models
