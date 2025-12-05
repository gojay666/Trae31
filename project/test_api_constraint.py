import requests
import json

# 测试添加站点规则的API
url = 'http://localhost:5000/admin/api/rules'

# 测试数据：使用已存在的site_name
payload = {
    'site_name': '四川发布',
    'site_url': 'https://www.new-test.com/',
    'title_xpath': '//title',
    'content_xpath': '//content',
    'request_headers': json.dumps({}),
    'is_active': '1'
}

print("测试添加重复的site_name...")
response = requests.post(url, data=payload)
print(f"状态码: {response.status_code}")
print(f"响应内容: {response.json()}")

# 测试数据：使用新的site_name
payload_new = {
    'site_name': '新站点测试',
    'site_url': 'https://www.new-test.com/',
    'title_xpath': '//title',
    'content_xpath': '//content',
    'request_headers': json.dumps({}),
    'is_active': '1'
}

print("\n测试添加新的site_name...")
response_new = requests.post(url, data=payload_new)
print(f"状态码: {response_new.status_code}")
print(f"响应内容: {response_new.json()}")
