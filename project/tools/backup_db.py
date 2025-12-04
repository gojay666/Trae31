#!/usr/bin/env python3
"""
数据库备份脚本
"""

import os
import sys
import datetime
import shutil
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def backup_db():
    """备份数据库"""
    # 加载环境变量
    load_dotenv()
    
    # 获取数据库URL
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print('错误: 未设置DATABASE_URL环境变量')
        return False
    
    # 创建备份目录
    backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    # 生成备份文件名
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if database_url.startswith('sqlite:///'):
        # SQLite数据库备份
        db_file = database_url.replace('sqlite:///', '')
        if not os.path.exists(db_file):
            print(f'错误: 数据库文件不存在: {db_file}')
            return False
        
        backup_file = os.path.join(backup_dir, f'sqlite_backup_{timestamp}.db')
        shutil.copy2(db_file, backup_file)
        print(f'SQLite数据库已备份到: {backup_file}')
        
    elif database_url.startswith('mysql://') or database_url.startswith('mysql+pymysql://'):
        # MySQL数据库备份
        import pymysql
        from urllib.parse import urlparse
        
        # 解析数据库URL
        parsed_url = urlparse(database_url)
        dbname = parsed_url.path[1:]  # 去掉开头的/        
        username = parsed_url.username
        password = parsed_url.password
        host = parsed_url.hostname
        port = parsed_url.port or 3306
        
        backup_file = os.path.join(backup_dir, f'mysql_backup_{timestamp}.sql')
        
        # 使用mysqldump命令备份
        command = f'mysqldump -h {host} -P {port} -u {username} -p{password} {dbname} > {backup_file}'
        os.system(command)
        print(f'MySQL数据库已备份到: {backup_file}')
        
    elif database_url.startswith('postgresql://'):
        # PostgreSQL数据库备份
        import psycopg2
        from urllib.parse import urlparse
        
        # 解析数据库URL
        parsed_url = urlparse(database_url)
        dbname = parsed_url.path[1:]  # 去掉开头的/        
        username = parsed_url.username
        password = parsed_url.password
        host = parsed_url.hostname
        port = parsed_url.port or 5432
        
        backup_file = os.path.join(backup_dir, f'postgresql_backup_{timestamp}.sql')
        
        # 使用pg_dump命令备份
        command = f'pg_dump -h {host} -p {port} -U {username} -d {dbname} > {backup_file}'
        os.system(f'PGPASSWORD={password} {command}')
        print(f'PostgreSQL数据库已备份到: {backup_file}')
        
    else:
        print(f'错误: 不支持的数据库类型: {database_url}')
        return False
    
    return True


if __name__ == '__main__':
    backup_db()
