import requests
from bs4 import BeautifulSoup

url = 'http://sc.news.cn/scyw.htm'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    response.encoding = 'utf-8'
    
    print(f"状态码: {response.status_code}")
    print(f"页面长度: {len(response.text)} 字符")
    
    # 保存页面内容到文件以便查看
    with open('xinhua_page.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("页面内容已保存到 xinhua_page.html")
    
    # 简单解析
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找所有a标签
    all_links = soup.find_all('a', href=True)
    print(f"\n找到 {len(all_links)} 个链接")
    
    # 查找包含新闻的链接（过滤条件）
    news_links = []
    for link in all_links:
        href = link.get('href')
        text = link.get_text(strip=True)
        
        if 'news.cn' in href and len(text) > 10:
            news_links.append((text, href))
    
    print(f"\n找到 {len(news_links)} 个可能的新闻链接:")
    for i, (text, href) in enumerate(news_links[:10]):
        print(f"\n链接 {i+1}:")
        print(f"  文本: {text}")
        print(f"  URL: {href}")
        
        # 检查是否包含时间戳格式
        if '2025-' in text:
            print(f"  包含时间戳: {text}")
            
            # 打印字符编码和详细信息
            print(f"  原始文本长度: {len(text)}")
            print(f"  字符编码: {[ord(c) for c in text]}")
            
except Exception as e:
    print(f"错误: {e}")
