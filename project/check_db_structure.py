import sqlite3
import os

# 数据库文件路径
db_path = 'instance/app.db'

# 检查数据库文件是否存在
if not os.path.exists(db_path):
    print(f"数据库文件不存在: {db_path}")
    exit()

# 连接到数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== 数据库表结构检查 ===")

# 查看site_rules表的创建语句
try:
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='site_rules'")
    table_info = cursor.fetchone()
    if table_info:
        print("site_rules表创建语句:")
        print(table_info[0])
    else:
        print("site_rules表不存在")
except Exception as e:
    print(f"查询site_rules表结构失败: {e}")

print("\n=== 表中的唯一约束 ===")

# 查看site_rules表的索引信息，包括唯一约束
try:
    cursor.execute("PRAGMA index_list('site_rules')")
    indexes = cursor.fetchall()
    for index in indexes:
        print(f"索引ID: {index[0]}, 名称: {index[1]}, 唯一: {index[2]}, 部分: {index[3]}, 排序: {index[4]}")
        # 查看索引列
        cursor.execute(f"PRAGMA index_info('{index[1]}')")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - 列: {col[2]}")
except Exception as e:
    print(f"查询索引信息失败: {e}")

print("\n=== 表中现有数据 ===")

# 查看site_rules表中的现有数据
try:
    cursor.execute("SELECT id, site_name, site_url FROM site_rules")
    rows = cursor.fetchall()
    print(f"共找到 {len(rows)} 条数据:")
    for row in rows:
        print(f"ID: {row[0]}, 站点名称: {row[1]}, 站点URL: {row[2]}")
except Exception as e:
    print(f"查询数据失败: {e}")

# 关闭连接
conn.close()
