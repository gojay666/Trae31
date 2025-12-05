from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager
from sqlalchemy.ext.declarative import declared_attr
import json


@login_manager.user_loader
def load_user(user_id):
    """根据用户ID加载用户"""
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    """用户模型"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<User {self.username}>"
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        """检查用户是否为管理员"""
        # 开发阶段，所有登录用户都是管理员
        return self.is_authenticated

    @is_admin.setter
    def is_admin(self, value):
        """设置用户为管理员或普通用户"""
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            # 如果管理员角色不存在，创建一个
            admin_role = Role(
                name='admin',
                description='系统管理员',
                permissions=['user_manage', 'role_manage', 'system_manage']
            )
            db.session.add(admin_role)
            db.session.commit()
        
        # 获取普通用户角色
        user_role = Role.query.filter_by(name='user').first()
        if not user_role:
            # 如果普通用户角色不存在，创建一个
            user_role = Role(
                name='user',
                description='普通用户',
                permissions=['report_view']
            )
            db.session.add(user_role)
            db.session.commit()
        
        # 根据value值设置用户角色
        if value:
            # 设置为管理员
            if admin_role not in self.roles:
                self.roles.append(admin_role)
            if user_role in self.roles:
                self.roles.remove(user_role)
        else:
            # 设置为普通用户
            if admin_role in self.roles:
                self.roles.remove(admin_role)
            if user_role not in self.roles:
                self.roles.append(user_role)


class BaseModel(db.Model):
    """基础模型，包含通用字段"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    @declared_attr
    def creator(cls):
        backref_name = f'{cls.__tablename__}_created_by'
        return db.relationship('User', foreign_keys=[cls.created_by], backref=db.backref(backref_name, lazy='dynamic'))
    
    @declared_attr
    def updater(cls):
        backref_name = f'{cls.__tablename__}_updated_by'
        return db.relationship('User', foreign_keys=[cls.updated_by], backref=db.backref(backref_name, lazy='dynamic'))


# 用户-角色关联表
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)


class Role(db.Model):
    """角色模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    permissions = db.Column(db.Text, nullable=True)  # JSON格式存储权限列表
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 多对多关系
    users = db.relationship('User', secondary=user_roles, lazy='subquery',
                           backref=db.backref('roles', lazy=True))
    
    def __repr__(self):
        return f"<Role {self.name}>"
    
    def set_permissions(self, permissions):
        """设置权限列表"""
        self.permissions = json.dumps(permissions)
    
    def get_permissions(self):
        """获取权限列表"""
        if not self.permissions:
            return []
        try:
            return json.loads(self.permissions)
        except:
            return []
    
    def has_permission(self, permission):
        """检查是否有指定权限"""
        permissions = self.get_permissions()
        return permission in permissions





class SystemConfig(BaseModel):
    """系统配置模型"""
    __tablename__ = 'system_config'
    
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(20), nullable=False, default='string')  # string, int, float, boolean, json
    label = db.Column(db.String(100), nullable=True)
    description = db.Column(db.String(200), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f"<SystemConfig {self.key}: {self.value}>"
    
    def get_value(self):
        """根据类型获取值"""
        if not self.value:
            return None
        
        try:
            if self.type == 'int':
                return int(self.value)
            elif self.type == 'float':
                return float(self.value)
            elif self.type == 'boolean':
                return self.value.lower() in ('true', 'yes', '1')
            elif self.type == 'json':
                return json.loads(self.value)
            else:
                return self.value
        except:
            return self.value
    
    def set_value(self, value):
        """根据类型设置值"""
        if value is None:
            self.value = None
        elif isinstance(value, (int, float, bool)):
            self.value = str(value)
        elif isinstance(value, (dict, list)):
            self.value = json.dumps(value)
        else:
            self.value = str(value)
    
    @classmethod
    def get_config(cls):
        """获取所有系统配置"""


class CrawlerTask(BaseModel):
    """数据采集任务模型"""
    __tablename__ = 'crawler_tasks'
    
    name = db.Column(db.String(100), nullable=False, comment='任务名称')
    description = db.Column(db.Text, nullable=True, comment='任务描述')
    url = db.Column(db.String(500), nullable=False, comment='采集URL')
    method = db.Column(db.String(10), nullable=False, default='GET', comment='请求方法')
    headers = db.Column(db.Text, nullable=True, comment='请求头(JSON格式)')
    params = db.Column(db.Text, nullable=True, comment='请求参数(JSON格式)')
    data = db.Column(db.Text, nullable=True, comment='请求数据(JSON格式)')
    rule = db.Column(db.Text, nullable=False, comment='采集规则(JSON格式)')
    status = db.Column(db.String(20), nullable=False, default='pending', comment='任务状态：pending(待执行), running(执行中), completed(已完成), failed(失败)')
    interval = db.Column(db.Integer, nullable=False, default=86400, comment='采集间隔(秒)')
    last_run_time = db.Column(db.DateTime, nullable=True, comment='最后执行时间')
    next_run_time = db.Column(db.DateTime, nullable=True, comment='下次执行时间')
    total_runs = db.Column(db.Integer, nullable=False, default=0, comment='总执行次数')
    success_runs = db.Column(db.Integer, nullable=False, default=0, comment='成功执行次数')
    failed_runs = db.Column(db.Integer, nullable=False, default=0, comment='失败执行次数')
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, comment='创建者ID')
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, comment='更新者ID')
    
    def __repr__(self):
        return f"<CrawlerTask {self.name} - {self.status}>"
    
    def get_headers(self):
        """获取请求头"""
        if not self.headers:
            return {}
        try:
            return json.loads(self.headers)
        except:
            return {}
    
    def set_headers(self, headers):
        """设置请求头"""
        self.headers = json.dumps(headers)
    
    def get_params(self):
        """获取请求参数"""
        if not self.params:
            return {}
        try:
            return json.loads(self.params)
        except:
            return {}
    
    def set_params(self, params):
        """设置请求参数"""
        self.params = json.dumps(params)
    
    def get_data(self):
        """获取请求数据"""
        if not self.data:
            return {}
        try:
            return json.loads(self.data)
        except:
            return {}
    
    def set_data(self, data):
        """设置请求数据"""
        self.data = json.dumps(data)
    
    def get_rule(self):
        """获取采集规则"""
        if not self.rule:
            return {}
        try:
            return json.loads(self.rule)
        except:
            return {}
    
    def set_rule(self, rule):
        """设置采集规则"""
        self.rule = json.dumps(rule)


class CrawlerResult(BaseModel):
    """数据采集结果模型"""
    __tablename__ = 'crawler_results'
    
    task_id = db.Column(db.Integer, db.ForeignKey('crawler_tasks.id'), nullable=False, comment='任务ID')
    task = db.relationship('CrawlerTask', backref=db.backref('results', lazy='dynamic'))
    url = db.Column(db.String(500), nullable=False, comment='采集URL')
    status_code = db.Column(db.Integer, nullable=False, comment='响应状态码')
    response_headers = db.Column(db.Text, nullable=True, comment='响应头(JSON格式)')
    response_body = db.Column(db.Text, nullable=True, comment='响应内容')
    extracted_data = db.Column(db.Text, nullable=True, comment='提取的数据(JSON格式)')
    execution_time = db.Column(db.Float, nullable=False, default=0.0, comment='执行时间(秒)')
    error_message = db.Column(db.Text, nullable=True, comment='错误信息')
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, comment='创建者ID')
    
    def __repr__(self):
        return f"<CrawlerResult Task: {self.task_id} - Status: {self.status_code}>"
    
    def get_response_headers(self):
        """获取响应头"""
        if not self.response_headers:
            return {}
        try:
            return json.loads(self.response_headers)
        except:
            return {}
    
    def set_response_headers(self, headers):
        """设置响应头"""
        self.response_headers = json.dumps(headers)
    
    def get_extracted_data(self):
        """获取提取的数据"""
        if not self.extracted_data:
            return {}
        try:
            return json.loads(self.extracted_data)
        except:
            return {}
    
    def set_extracted_data(self, data):
        """设置提取的数据"""
        self.extracted_data = json.dumps(data)
        configs = cls.query.filter_by(is_active=True).all()
        config_dict = {}
        for config in configs:
            config_dict[config.key] = config.get_value()
        return config_dict
    
    @classmethod
    def get_by_key(cls, key, default=None):
        """根据键获取配置值"""
        config = cls.query.filter_by(key=key, is_active=True).first()
        if config:
            return config.get_value()
        return default
    
    @classmethod
    def set_by_key(cls, key, value, type='string', label=None, description=None):
        """根据键设置配置值"""
        config = cls.query.filter_by(key=key).first()
        if config:
            config.set_value(value)
            config.type = type
            if label:
                config.label = label
            if description:
                config.description = description
        else:
            config = cls(
                key=key,
                type=type,
                label=label,
                description=description
            )
            config.set_value(value)
            db.session.add(config)
        
        try:
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False


class CrawlResult(BaseModel):
    """数据采集结果模型"""
    __tablename__ = 'crawl_result'
    
    keyword = db.Column(db.String(100), nullable=False, comment='采集关键词')
    title = db.Column(db.String(255), nullable=False, comment='标题')
    summary = db.Column(db.Text, nullable=True, comment='摘要')
    cover = db.Column(db.String(500), nullable=True, comment='封面图片URL')
    original_url = db.Column(db.String(500), nullable=False, comment='原始URL')
    source = db.Column(db.String(100), nullable=True, comment='来源网站')
    depth_crawled = db.Column(db.Boolean, default=False, comment='是否已深度采集')
    is_stored = db.Column(db.Boolean, default=False, comment='是否已存储到数据库')
    raw_data = db.Column(db.Text, nullable=True, comment='原始采集数据')
    
    def __repr__(self):
        return f"<CrawlResult {self.title[:20]}>"


class DepthCrawlResult(BaseModel):
    """深度采集结果模型"""
    __tablename__ = 'depth_crawl_result'
    
    crawl_result_id = db.Column(db.Integer, db.ForeignKey('crawl_result.id'), nullable=False, comment='关联的采集结果ID')
    content = db.Column(db.Text, nullable=True, comment='深度采集内容')
    images = db.Column(db.Text, nullable=True, comment='采集到的图片列表（JSON格式）')
    videos = db.Column(db.Text, nullable=True, comment='采集到的视频列表（JSON格式）')
    links = db.Column(db.Text, nullable=True, comment='页面中的链接列表（JSON格式）')
    meta_data = db.Column(db.Text, nullable=True, comment='页面元数据（JSON格式）')
    
    # 关系
    crawl_result = db.relationship('CrawlResult', backref=db.backref('depth_results', lazy=True))
    
    def __repr__(self):
        return f"<DepthCrawlResult {self.crawl_result.title[:20]}>"
    
    def set_images(self, images):
        """设置图片列表"""
        if isinstance(images, list):
            self.images = json.dumps(images)
        else:
            self.images = images
    
    def get_images(self):
        """获取图片列表"""
        if not self.images:
            return []
        try:
            return json.loads(self.images)
        except:
            return []
    
    def set_videos(self, videos):
        """设置视频列表"""
        if isinstance(videos, list):
            self.videos = json.dumps(videos)
        else:
            self.videos = videos
    
    def get_videos(self):
        """获取视频列表"""
        if not self.videos:
            return []
        try:
            return json.loads(self.videos)
        except:
            return []
    
    def set_links(self, links):
        """设置链接列表"""
        if isinstance(links, list):
            self.links = json.dumps(links)
        else:
            self.links = links
    
    def get_links(self):
        """获取链接列表"""
        if not self.links:
            return []
        try:
            return json.loads(self.links)
        except:
            return []
    
    def set_meta_data(self, meta_data):
        """设置元数据"""
        if isinstance(meta_data, dict):
            self.meta_data = json.dumps(meta_data)
        else:
            self.meta_data = meta_data
    
    def get_meta_data(self):
        """获取元数据"""
        if not self.meta_data:
            return {}
        try:
            return json.loads(self.meta_data)
        except:
            return {}


class SiteRule(BaseModel):
    """站点采集规则模型"""
    __tablename__ = 'site_rules'
    
    site_name = db.Column(db.String(100), nullable=False, unique=True, comment='站点名称')
    site_url = db.Column(db.String(500), nullable=False, comment='站点URL')
    title_xpath = db.Column(db.String(200), nullable=False, comment='标题XPATH')
    content_xpath = db.Column(db.String(200), nullable=False, comment='详细内容XPATH')
    request_headers = db.Column(db.Text, nullable=True, comment='请求头(JSON格式)')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    
    def __repr__(self):
        return f"<SiteRule {self.site_name}>"
    
    def get_request_headers(self):
        """获取请求头"""
        if not self.request_headers:
            return {}
        try:
            return json.loads(self.request_headers)
        except:
            return {}
    
    def set_request_headers(self, headers):
        """设置请求头"""
        if isinstance(headers, dict):
            self.request_headers = json.dumps(headers)
        else:
            self.request_headers = headers


class AIEngine(BaseModel):
    """AI引擎模型"""
    __tablename__ = 'ai_engines'
    
    provider_name = db.Column(db.String(100), nullable=False, comment='服务商名称')
    api_url = db.Column(db.String(500), nullable=False, comment='API地址')
    api_key = db.Column(db.String(255), nullable=False, comment='API密钥')
    model_name = db.Column(db.String(100), nullable=False, comment='模型名称')
    description = db.Column(db.Text, nullable=True, comment='模型描述')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    api_params = db.Column(db.Text, nullable=True, comment='额外API参数(JSON格式)')
    icon = db.Column(db.String(100), nullable=True, comment='图标CSS类名')
    
    def __repr__(self):
        return f"<AIEngine {self.provider_name} - {self.model_name}>"
    
    def get_api_params(self):
        """获取额外API参数"""
        if not self.api_params:
            return {}
        try:
            return json.loads(self.api_params)
        except:
            return {}
    
    def set_api_params(self, params):
        """设置额外API参数"""
        if isinstance(params, dict):
            self.api_params = json.dumps(params)
        else:
            self.api_params = params
