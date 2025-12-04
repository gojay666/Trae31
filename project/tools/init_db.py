#!/usr/bin/env python3
"""
数据库初始化脚本
"""

import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, SystemConfig


def init_db():
    """初始化数据库"""
    # 加载环境变量
    load_dotenv()
    
    # 创建应用
    app = create_app(None)
    
    with app.app_context():
        # 创建数据库表
        print('正在创建数据库表...')
        db.create_all()
        
        # 检查是否已有管理员用户
        admin_user = User.query.filter_by(username='admin').first()
        
        if not admin_user:
            # 创建默认管理员用户
            print('正在创建默认管理员用户...')
            admin = User(username='admin', email='admin@example.com')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('默认管理员用户已创建: 用户名=admin, 密码=admin123')
        else:
            print('管理员用户已存在')
        
        # 检查并创建默认系统配置
        print('正在检查系统配置...')
        default_configs = [
            {'key': 'app_name', 'value': '企业管理系统', 'type': 'string', 'label': '应用名称', 'description': '系统应用名称'},
            {'key': 'app_description', 'value': '一个功能完善的企业管理系统', 'type': 'string', 'label': '应用描述', 'description': '系统应用描述'},
            {'key': 'copyright_info', 'value': '© 2023 企业管理系统', 'type': 'string', 'label': '版权信息', 'description': '系统版权信息'},
            {'key': 'icp_code', 'value': '粤ICP备12345678号', 'type': 'string', 'label': '备案号', 'description': '网站备案号'},
            {'key': 'logo_url', 'value': '', 'type': 'string', 'label': 'LOGO URL', 'description': '系统LOGO图片URL'},
        ]
        
        for config in default_configs:
            existing_config = SystemConfig.query.filter_by(key=config['key']).first()
            if not existing_config:
                new_config = SystemConfig(**config)
                db.session.add(new_config)
                print(f'添加默认配置: {config["key"]} = {config["value"]}')
            else:
                print(f'配置已存在: {config["key"]}')
        
        db.session.commit()
        print('数据库初始化完成！')


if __name__ == '__main__':
    init_db()
