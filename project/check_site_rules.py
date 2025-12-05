import sqlite3
import os

# 数据库文件路径
db_path = 'instance/app.db'

# 连接到数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== site_rules表中的所有数据 ===")

# 查询所有site_rules数据
try:
    cursor.execute("SELECT id, site_name, site_url, created_at FROM site_rules ORDER BY created_at DESC")
    rules = cursor.fetchall()
    
    if not rules:
        print("数据库中没有任何规则！")
    else:
        print(f"共找到 {len(rules)} 条规则：")
        for rule in rules:
            print(f"ID: {rule[0]}, 站点名称: {rule[1]}, URL: {rule[2]}, 创建时间: {rule[3]}")
        
        # 检查测试中添加的规则
        print("\n=== 检查测试中添加的规则 ===")
        cursor.execute("SELECT * FROM site_rules WHERE site_name='新站点测试'")
        test_rule = cursor.fetchone()
        if test_rule:
            print("找到测试规则：")
            print(f"ID: {test_rule[6]}, 站点名称: {test_rule[0]}, URL: {test_rule[1]}")
        else:
            print("没有找到测试规则！")
            
except Exception as e:
    print(f"查询数据失败: {e}")

# 关闭连接
conn.close()
