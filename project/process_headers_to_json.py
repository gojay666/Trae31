import json
import re
from app import create_app, db
from app.models import SiteRule

# 原始请求头文本
raw_headers = """accept
 text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
 accept-encoding
 gzip, deflate, br, zstd
 accept-language
 zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
 cache-control
 max-age=0
 connection
 keep-alive
 cookie
 nouse=nouse; costumerid=costumeridprifixgKCNaUwwk; costumeridprifixgKCNaUwwk=0; ValidateNumber="ka8gdFXDbx8="
 host
 www.scpublic.cn
 referer
 `https://www.scpublic.cn/` 
 sec-ch-ua
 "Chromium";v="142", "Microsoft Edge";v="142", "Not_A Brand";v="99"
 sec-ch-ua-mobile
 ?0
 sec-ch-ua-platform
 "Windows"
 sec-fetch-dest
 document
 sec-fetch-mode
 navigate
 sec-fetch-site
 same-origin
 sec-fetch-user
 ?1
 upgrade-insecure-requests
 1
 user-agent
 Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0"""

def parse_headers(raw_text):
    """解析原始请求头文本为字典"""
    # 移除首尾空白
    raw_text = raw_text.strip()
    
    # 分割成键值对行（处理每行是键，下一行是值的格式）
    lines = raw_text.split('\n')
    headers_dict = {}
    
    i = 0
    while i < len(lines):
        # 获取键（去除空白）
        key = lines[i].strip()
        if key:
            # 下一行是值
            i += 1
            if i < len(lines):
                value = lines[i].strip()
                # 移除可能的反引号
                value = value.replace('`', '')
                headers_dict[key] = value
        i += 1
    
    return headers_dict

def convert_to_json(headers_dict):
    """将字典转换为JSON字符串"""
    return json.dumps(headers_dict, indent=2, ensure_ascii=False)

def store_to_database(headers_json):
    """将JSON数据存储到数据库"""
    app = create_app()
    
    with app.app_context():
        # 创建或更新站点规则
        # 检查是否已存在该站点的规则
        rule = SiteRule.query.filter_by(site_url='https://www.scpublic.cn/').first()
        
        if rule:
            # 更新现有规则
            rule.request_headers = headers_json
            rule.updated_at = db.func.now()
            print(f"更新现有规则：ID={rule.id}, 站点={rule.site_name}")
        else:
            # 创建新规则
            rule = SiteRule(
                site_name='四川发布',
                site_url='https://www.scpublic.cn/',
                title_xpath='//h1',  # 基本的标题XPath，可根据实际页面结构调整
                content_xpath='//div[@class="content"]',  # 基本的内容XPath，可根据实际页面结构调整
                request_headers=headers_json
            )
            db.session.add(rule)
            print("创建新规则：四川发布")
        
        # 提交到数据库
        db.session.commit()
        print("规则已成功存储到数据库！")
        return rule.id

def save_to_file(headers_json, filename='headers.json'):
    """将JSON数据保存到文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(headers_json)
    print(f"JSON数据已保存到文件：{filename}")

def main():
    """主函数"""
    print("=== 请求头转换和存储工具 ===")
    
    # 1. 解析请求头
    print("\n1. 解析请求头...")
    headers_dict = parse_headers(raw_headers)
    print(f"   解析完成，共 {len(headers_dict)} 个请求头字段")
    
    # 2. 转换为JSON
    print("\n2. 转换为JSON格式...")
    headers_json = convert_to_json(headers_dict)
    print("   JSON转换完成")
    print(f"\nJSON预览：\n{headers_json}")
    
    # 3. 保存到文件
    print("\n3. 保存到文件...")
    save_to_file(headers_json)
    
    # 4. 存储到数据库
    print("\n4. 存储到数据库...")
    try:
        rule_id = store_to_database(headers_json)
        print(f"   数据库存储成功，规则ID：{rule_id}")
    except Exception as e:
        print(f"   数据库存储失败：{e}")
        print("   请确保应用已正确配置数据库连接")
    
    print("\n=== 操作完成 ===")

if __name__ == "__main__":
    main()
