import requests
from bs4 import BeautifulSoup

# 设置请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0'
}

# 发送请求
try:
    response = requests.get('https://www.baidu.com/s?wd=西昌', headers=headers, timeout=10)
    print(f"Status code: {response.status_code}")
    print(f"Content encoding: {response.encoding}")
    
    # 手动设置编码
    response.encoding = 'utf-8'
    
    # 保存到文件
    with open('baidu_result.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print(f"Saved {len(response.text)} characters to baidu_result.html")
    
    # 简单解析测试
    soup = BeautifulSoup(response.text, 'html.parser')
    print(f"Title: {soup.title.string if soup.title else 'No title found'}")
    
    # 查找所有div标签
    divs = soup.find_all('div', limit=10)
    print(f"Found {len(divs)} div tags (showing first 5):")
    for i, div in enumerate(divs[:5]):
        print(f"Div {i+1} class: {div.get('class')}, id: {div.get('id')}")
        
except Exception as e:
    print(f"Error: {e}")
