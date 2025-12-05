import requests
import json

# 测试API响应格式
url = 'http://localhost:5000/admin/api/rules?page=1&limit=10'

print(f"正在请求: {url}")
try:
    response = requests.get(url)
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        # 解析响应内容
        data = response.json()
        print("\n=== API响应格式 ===")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # 检查响应格式是否符合Layui表格要求
        required_fields = ['code', 'msg', 'count', 'data']
        has_required_fields = all(field in data for field in required_fields)
        print(f"\n是否包含Layui表格所需的所有字段: {'是' if has_required_fields else '否'}")
        
        if has_required_fields:
            print(f"\n=== 规则数据 ===")
            print(f"总规则数: {data['count']}")
            print(f"当前页规则数: {len(data['data'])}")
            
            if data['data']:
                print("\n规则列表:")
                for rule in data['data']:
                    print(f"ID: {rule['id']}, 站点名称: {rule['site_name']}, URL: {rule['site_url']}")
            else:
                print("\n没有找到任何规则!")
    else:
        print(f"请求失败: {response.reason}")
        
except Exception as e:
    print(f"请求出错: {str(e)}")
