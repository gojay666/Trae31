from flask import current_app
from app import create_app, db

# 创建应用实例
app = create_app()

# 进入应用上下文
with app.app_context():
    print("=== 应用配置信息 ===")
    print(f"应用根路径: {app.root_path}")
    print(f"数据库连接字符串: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"模板文件夹: {app.template_folder}")
    print(f"静态文件夹: {app.static_folder}")
    
    # 检查数据库连接
    try:
        # 尝试获取数据库连接
        with db.engine.connect() as conn:
            print("\n=== 数据库连接成功 ===")
            # 查询当前数据库中的表
            result = conn.execute(db.text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
            tables = result.fetchall()
            print(f"数据库中共有 {len(tables)} 个表：")
            for table in tables:
                print(f"- {table[0]}")
            
            # 检查site_rules表中的数据
            print("\n=== site_rules表中的数据 ===")
            try:
                result = conn.execute(db.text("SELECT id, site_name, site_url FROM site_rules ORDER BY created_at DESC"))
                rules = result.fetchall()
                if not rules:
                    print("没有任何规则！")
                else:
                    print(f"共找到 {len(rules)} 条规则：")
                    for rule in rules:
                        print(f"ID: {rule[0]}, 站点名称: {rule[1]}, URL: {rule[2]}")
            except Exception as e:
                print(f"查询site_rules表失败: {e}")
                
    except Exception as e:
        print(f"\n数据库连接失败: {e}")
