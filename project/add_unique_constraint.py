import sqlite3

# 连接到数据库
db_path = 'instance/app.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("尝试为site_rules表的site_name字段添加唯一约束...")

try:
    # 为site_name字段添加唯一约束
    cursor.execute("CREATE UNIQUE INDEX idx_site_rules_site_name ON site_rules(site_name)")
    conn.commit()
    print("成功添加唯一约束!")
    
    # 验证约束是否已创建
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='site_rules' AND sql LIKE '%site_name%'")
    index = cursor.fetchone()
    if index:
        print(f"验证: 已找到索引 {index[0]}")
    
    # 测试约束是否生效
    print("\n测试约束是否生效...")
    try:
        # 尝试插入一个与现有site_name相同的记录
        cursor.execute("INSERT INTO site_rules (site_name, site_url, title_xpath, content_xpath) VALUES (?, ?, ?, ?)", 
                      ('四川发布', 'https://www.test.com/', '//title', '//content'))
        conn.commit()
        print("错误: 插入成功了，但应该失败！")
    except sqlite3.IntegrityError as e:
        conn.rollback()
        print(f"成功: 插入失败，符合预期的唯一约束错误: {e}")
        
except sqlite3.OperationalError as e:
    if "already exists" in str(e):
        print("约束已经存在，无需重复添加")
    else:
        print(f"添加约束失败: {e}")
finally:
    # 关闭连接
    conn.close()
