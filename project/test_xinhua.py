import requests
from bs4 import BeautifulSoup
import re

# 目标URL
url = 'http://sc.news.cn/scyw.htm'

# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0'
}

try:
    # 发送请求
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    response.encoding = 'utf-8'
    
    print('状态码:', response.status_code)
    print('页面编码:', response.encoding)
    print('页面长度:', len(response.text))
    
    # 解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找所有div标签及其类名
    div_classes = []
    for div in soup.find_all('div', class_=True):
        classes = div.get('class')
        if classes and isinstance(classes, list):
            div_classes.extend(classes)
        elif classes:
            div_classes.append(classes)
    
    print('\n所有div类名:', list(set(div_classes)))
    
    # 查找所有ul标签及其类名
    ul_classes = []
    for ul in soup.find_all('ul', class_=True):
        classes = ul.get('class')
        if classes and isinstance(classes, list):
            ul_classes.extend(classes)
        elif classes:
            ul_classes.append(classes)
    
    print('\n所有ul类名:', list(set(ul_classes)))
    
    # 查找所有可能包含新闻的容器
    print('\n=== 查找新闻列表 ===')
    
    # 方式1: 查找包含特定类名的ul或div
    news_containers = []
    
    # 尝试查找包含新闻的ul
    ul_containers = soup.find_all('ul')
    print('找到的ul数量:', len(ul_containers))
    
    # 查找包含新闻链接的ul
    for i, ul in enumerate(ul_containers):
        links = ul.find_all('a', href=True)
        if len(links) > 10:
            print(f'ul {i} 包含 {len(links)} 个链接')
            news_containers.append(ul)
    
    # 方式2: 查找包含时间戳的元素
    time_pattern = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
    time_elements = soup.find_all(string=time_pattern)
    print('\n找到包含时间戳的元素数量:', len(time_elements))
    
    # 查看时间元素的父元素结构
    if time_elements:
        print('\n时间元素的父元素结构:')
        for i, elem in enumerate(time_elements[:3]):
            parent = elem.parent
            print(f'第{i+1}个时间元素的父元素:', parent.name)
            print(f'父元素的类名:', parent.get('class'))
            print(f'祖父元素:', parent.parent.name)
            print(f'祖父元素的类名:', parent.parent.get('class'))
    
    # 方式3: 直接查找所有包含新闻.cn的链接
    news_links = []
    all_links = soup.find_all('a', href=True)
    for link in all_links:
        href = link.get('href')
        text = link.get_text(strip=True)
        if href and 'news.cn' in href and len(text) > 10:
            news_links.append((text, href))
    
    print('\n找到的新闻链接数量:', len(news_links))
    
    if news_links:
        print('\n前5条新闻链接:')
        for i, (text, href) in enumerate(news_links[:5]):
            print(f'{i+1}. 标题: {text[:50]}...')
            print(f'   链接: {href}')
            print(f'   包含时间戳: {bool(time_pattern.search(text))}')

except requests.RequestException as e:
    print('请求失败:', e)
except Exception as e:
    print('解析失败:', e)
