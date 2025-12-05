import sqlite3
import os

# 数据库文件路径
db_path = 'instance/app.db'

# 连接到数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== 数据库完整结构检查 ===")

# 查看所有表
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    print(f"\n共找到 {len(tables)} 个表:")
    for table in tables:
        print(f"- {table[0]}")
except Exception as e:
    print(f"查询表列表失败: {e}")

print("\n=== site_rules表的完整信息 ===")

# 查看site_rules表的详细结构
try:
    cursor.execute("PRAGMA table_info('site_rules')")
    columns = cursor.fetchall()
    print("表结构:")
    for col in columns:
        print(f"- ID: {col[0]}, 名称: {col[1]}, 类型: {col[2]}, 非空: {col[3]}, 默认值: {col[4]}, 主键: {col[5]}")
except Exception as e:
    print(f"查询表结构失败: {e}")

# 查看所有索引和约束
try:
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='site_rules' ORDER BY name")
    indexes = cursor.fetchall()
    print("\n索引和约束:")
    for idx in indexes:
        print(f"- 名称: {idx[0]}")
        print(f"  SQL: {idx[1]}")
except Exception as e:
    print(f"查询索引失败: {e}")

# 查看最近的错误日志
print("\n=== 最近的数据库操作日志 ===")
print("注意: SQLite默认不记录操作日志，此功能需要特殊配置")

# 尝试重新创建一个简单的插入来测试约束
try:
    print("\n=== 测试插入操作 ===")
    # 尝试插入一个与现有site_name相同的记录
    cursor.execute("INSERT INTO site_rules (site_name, site_url, title_xpath, content_xpath) VALUES (?, ?, ?, ?)", 
                  ('四川发布', 'https://www.test.com/', '//title', '//content'))
    conn.commit()
    print("插入成功? 这说明site_name的唯一约束可能有问题")
except sqlite3.IntegrityError as e:
    conn.rollback()
    print(f"插入失败(预期的site_name唯一约束错误): {e}")

try:
    # 尝试插入一个与现有site_url相同但site_name不同的记录
    cursor.execute("INSERT INTO site_rules (site_name, site_url, title_xpath, content_xpath) VALUES (?, ?, ?, ?)", 
                  ('测试站点', 'www.scpublic.cn', '//title', '//content'))
    conn.commit()
    print("插入成功(预期的site_url无唯一约束)")
    # 清理测试数据
    cursor.execute("DELETE FROM site_rules WHERE site_name='测试站点'")
    conn.commit()
except sqlite3.IntegrityError as e:
    conn.rollback()
    print(f"插入失败(意外的site_url唯一约束错误): {e}")

# 关闭连接
conn.close()
