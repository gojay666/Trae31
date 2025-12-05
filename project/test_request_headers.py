import requests
import json

# 测试用的原始请求头格式
raw_headers = '''User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Accept-Encoding: gzip, deflate, br, zstd
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
Connection: keep-alive
Host: www.example.com
Upgrade-Insecure-Requests: 1'''

# 测试用的JSON格式请求头
json_headers = json.dumps({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif",
    "Host": "www.test.com"
})

def test_add_rule_with_raw_headers():
    """测试使用原始请求头格式添加规则"""
    print("\n=== 测试1：使用原始请求头格式添加规则 ===")
    url = 'http://localhost:5000/admin/api/rules'
    
    data = {
        'site_name': '原始请求头测试站点',
        'site_url': 'http://www.rawheaders.com',
        'title_xpath': '//h1',
        'content_xpath': '//div[@class="content"]',
        'request_headers': raw_headers,
        'is_active': '1'
    }
    
    try:
        response = requests.post(url, data=data)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        return response.json().get('success', False)
    except Exception as e:
        print(f"测试失败: {e}")
        return False

def test_add_rule_with_json_headers():
    """测试使用JSON格式请求头添加规则"""
    print("\n=== 测试2：使用JSON格式请求头添加规则 ===")
    url = 'http://localhost:5000/admin/api/rules'
    
    data = {
        'site_name': 'JSON请求头测试站点',
        'site_url': 'http://www.jsonheaders.com',
        'title_xpath': '//h1',
        'content_xpath': '//div[@class="content"]',
        'request_headers': json_headers,
        'is_active': '1'
    }
    
    try:
        response = requests.post(url, data=data)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        return response.json().get('success', False)
    except Exception as e:
        print(f"测试失败: {e}")
        return False

def test_view_rules():
    """查看所有规则，验证请求头是否正确存储"""
    print("\n=== 测试3：查看所有规则 ===")
    url = 'http://localhost:5000/admin/api/rules'
    
    try:
        response = requests.get(url)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"共找到 {data['count']} 条规则")
            
            # 查找刚刚添加的两条测试规则
            for rule in data['data']:
                if '原始请求头测试站点' in rule['site_name'] or 'JSON请求头测试站点' in rule['site_name']:
                    print(f"\n规则: {rule['site_name']}")
                    print(f"请求头: {json.dumps(rule['request_headers'], indent=2, ensure_ascii=False)}")
                    print(f"请求头类型: {type(rule['request_headers']).__name__}")
        
        return True
    except Exception as e:
        print(f"测试失败: {e}")
        return False

if __name__ == '__main__':
    print("开始测试请求头解析功能...")
    
    # 测试1：使用原始请求头格式添加规则
    test_add_rule_with_raw_headers()
    
    # 测试2：使用JSON格式请求头添加规则
    test_add_rule_with_json_headers()
    
    # 测试3：查看所有规则
    test_view_rules()
    
    print("\n测试完成！")
