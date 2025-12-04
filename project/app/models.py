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
        # 检查用户是否有管理员角色
        for role in self.roles:
            if role.name == 'admin':
                return True
        return False

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
        return db.relationship('User', foreign_keys=[cls.created_by], backref=db.backref('created_records', lazy='dynamic'))
    
    @declared_attr
    def updater(cls):
        return db.relationship('User', foreign_keys=[cls.updated_by], backref=db.backref('updated_records', lazy='dynamic'))


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
