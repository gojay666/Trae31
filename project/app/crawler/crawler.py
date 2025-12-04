import requests
import urllib.parse
from bs4 import BeautifulSoup
import re

def crawl_baidu_search(keyword, pn=0):
    """
    从百度搜索抓取指定关键字的结果（真实爬虫版本）
    
    Args:
        keyword: 搜索关键字
        pn: 翻页参数，默认为0代表第1页，10代表第2页，20代表第3页，以此类推
    
    Returns:
        list: 包含抓取结果的列表，每个结果包含标题、概要、封面、原始URL和来源
    """
    print(f"Crawling Baidu for keyword: {keyword}, pn: {pn}")
    
    # 计算当前页码
    page = pn // 10 + 1
    
    # 构建请求URL
    base_url = "https://www.baidu.com/s"
    params = {
        'wd': keyword,
        'rsv_spt': '1',
        'rsv_iqid': '0xa1da5d3e000106fb',
        'issp': '1',
        'f': '8',
        'rsv_bp': '1',
        'rsv_idx': '2',
        'ie': 'utf-8',
        'rqlang': 'cn',
        'tn': 'baiduhome_pg',
        'rsv_enter': '1',
        'rsv_dl': 'tb',
        'pn': pn
    }
    
    # 设置请求头（更完整的请求头信息）
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'max-age=0',
        'connection': 'keep-alive',
        'cookie': 'BAIDUID_BFESS=67137812AA67AE09E42FC5302AD89A71:FG=1; __bid_n=18bbf08dae11376dcf5d5b; BIDUPSID=67137812AA67AE09E42FC5302AD89A71; PSTM=1745070352; COOKIE_SESSION=42962283_0_0_2_6_0_1_0_0_0_0_0_34_0_58_0_1745070415_0_1745070357%7C2%230_0_1745070357%7C1; RT="z=1&dm=baidu.com&si=183a759d-baaf-494e-beb8-50f95cc6b7af&ss=mik85no1&sl=2&tt=6g2&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=41lg&ul=42a1&hd=42a2"; BDUSS=hxdXc0YlZzcXk5ZHkxWERaeDNxekVpdnNpbWY0YnA5azN2d2tjWnFMNXRFMVpwSVFBQUFBJCQAAAAAAQAAAAEAAAAqtv03Z3lqMjg3MjgwNTc1MgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAG2GLmlthi5pZD; BDUSS_BFESS=hxdXc0YlZzcXk5ZHkxWERaeDNxekVpdnNpbWY0YnA5azN2d2tjWnFMNXRFMVpwSVFBQUFBJCQAAAAAAQAAAAEAAAAqtv03Z3lqMjg3MjgwNTc1MgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAG2GLmlthi5pZD; BD_UPN=12314753; BA_HECTOR=a0a120a00kalah0l8501040k0g8kai1kj1n7f25; ZFY=2hC99dJP0YapLd:BtmyZ2E8tXBcROehH6hwhNZtarF7Y:C; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; BD_CK_SAM=1; PSINO=1; H_PS_PSSID=60274_63147_66121_66208_66191_66231_66246_66169_66275_66253_66393_66467_66529_66545_66584_66594_66604_66611_66655_66664_66679_66671_66667_66694_66695_66688_66716_66773_66784_66792_66747_66802_66805; delPer=1; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; H_WISE_SIDS=60274_63147_66121_66208_66191_66231_66246_66169_66275_66253_66393_66467_66529_66545_66584_66594_66604_66611_66655_66664_66679_66671_66667_66694_66695_66688_66716_66773_66784_66792_66747_66802_66805; H_PS_645EC=c4ce8a2s4n01VFnA1tdoia2fhaNPAI51TOh%2BpZxOYoSnog%2FR9eLej%2BZH8zVfHkzmU9vo; baikeVisitId=7067bd1c-8420-4926-80a0-9da5874f32f6; BDSVRTM=491',
        'host': 'www.baidu.com',
        'sec-ch-ua': '"Chromium";v="142", "Microsoft Edge";v="142", "Not_A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0'
    }
    
    try:
        # 发送请求，让requests自动处理压缩的响应
        response = requests.get(base_url, params=params, headers=headers, timeout=10, 
                              allow_redirects=True, 
                              stream=False)  # stream=False让requests自动处理压缩
        response.raise_for_status()  # 检查请求是否成功
        
        # 强制使用utf-8编码，处理中文乱码问题
        response.encoding = 'utf-8'
        html_text = response.text.encode('utf-8').decode('utf-8', 'ignore')
        
        print(f"响应编码: {response.encoding}")
        print(f"响应头: {dict(response.headers)}")
        
        # 解析HTML
        soup = BeautifulSoup(html_text, 'html.parser')
        
        # 查找搜索结果
        results = []
        
        # 打印响应内容的前500个字符，用于调试HTML结构
        print(f"响应内容前500字符: {html_text[:500]}...")
        
        # 尝试使用不同的方式查找搜索结果区域
        results_containers = soup.find_all('div', class_=lambda x: x and ('result' in x or 'c-container' in x or 'content_right' in x))
        
        if not results_containers:
            # 尝试查找所有可能包含搜索结果的div
            results_containers = soup.find_all('div', style=True)
            print(f"找到 {len(results_containers)} 个带style的div")
        
        # 遍历所有可能的结果容器
        for result in results_containers:
            # 尝试获取标题
            title = ''
            
            # 首先尝试从h3标签获取标题（百度搜索结果的标准标题标签）
            h3_tag = result.find('h3')
            if h3_tag:
                title = h3_tag.get_text(strip=True)
            
            # 如果没有找到标题，尝试其他方式
            if not title or len(title) < 5:
                continue
            
            # 过滤掉不需要的结果
            skip_keywords = ['上一页', '下一页', '帮助', '搜索', '首页', '登录', '注册']
            if any(skip in title for skip in skip_keywords):
                continue
            
            # 过滤掉过短或无效的标题
            if len(title) < 10 or len(title) > 200:
                continue
            
            # 尝试获取原始URL
            original_url = ''
            link_tag = result.find('a')
            if link_tag:
                original_url = link_tag.get('href', '')
            
            # 处理百度跳转链接
            if original_url.startswith('/link?'):
                original_url = 'https://www.baidu.com' + original_url
            
            # 尝试获取概要
            summary = ''
            summary_tag = result.find('div', class_=re.compile(r'c-abstract|content'))
            if summary_tag:
                summary = summary_tag.get_text(strip=True)
            
            # 如果没有找到概要，尝试从其他元素获取
            if not summary or len(summary) < 20:
                text_tags = result.find_all(['div', 'p'])
                for tag in text_tags:
                    text = tag.get_text(strip=True)
                    if text and len(text) > 20 and text != title:
                        summary = text
                        break
            
            # 尝试获取来源
            source = ''
            source_tag = result.find('span', class_=re.compile(r'c-color-gray|c-showurl'))
            if not source_tag:
                source_tag = result.find('a', class_=re.compile(r'c-showurl'))
            if source_tag:
                source = source_tag.get_text(strip=True)
            
            # 尝试获取封面（图片）
            cover = ''
            img_tag = result.find('img')
            if img_tag:
                cover = img_tag.get('src', '')
                if cover and not cover.startswith('http'):
                    cover = 'https://www.baidu.com' + cover
            
            # 将结果添加到列表
            results.append({
                'title': title,
                'summary': summary,
                'cover': cover,
                'original_url': original_url,
                'source': source
            })
                
        # 如果还是没有找到结果，尝试使用更通用的方式
        if not results:
            print("使用备选方式查找结果")
            # 查找所有包含链接的元素
            all_links = soup.find_all('a')
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # 过滤掉不需要的链接
                if not text or len(text) < 15:
                    continue
                
                skip_keywords = ['上一页', '下一页', '帮助', '搜索', '首页', '登录', '注册']
                if any(skip in text for skip in skip_keywords):
                    continue
                
                if href.startswith('/') and not href.startswith('/link?'):
                    continue
                
                # 过滤掉百度内部链接
                if 'baidu.com' in href and 'link?' not in href:
                    continue
                
                # 尝试获取父元素中的文本作为概要
                parent = link.parent
                summary = ''
                if parent:
                    summary = parent.get_text(strip=True)
                    if summary == text:
                        grandparent = parent.parent
                        if grandparent:
                            summary = grandparent.get_text(strip=True)
                
                results.append({
                    'title': text,
                    'summary': summary,
                    'cover': '',
                    'original_url': href if href.startswith('http') else 'https://www.baidu.com' + href,
                    'source': ''
                })
        
        # 去重处理
        seen_titles = set()
        unique_results = []
        for item in results:
            if item['title'] not in seen_titles:
                seen_titles.add(item['title'])
                unique_results.append(item)
        
        # 进一步过滤掉无效结果
        final_results = []
        for item in unique_results:
            # 确保有基本的信息
            if item['title'] and (item['summary'] or item['source'] or item['original_url']):
                final_results.append(item)
        
        print(f"成功抓取到 {len(final_results)} 条有效结果")
        
        # 对结果进行编码处理，确保中文正确显示
        for result in final_results:
            # 确保所有字符串都是utf-8编码
            for key in result:
                if isinstance(result[key], str):
                    result[key] = result[key].encode('utf-8').decode('utf-8', 'ignore')
        
        return final_results
        
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return []
    except Exception as e:
        print(f"处理响应失败: {e}")
        return []

if __name__ == "__main__":
    # 测试代码
    test_keyword = "西昌"  # 确保中文关键字正确编码
    
    # 测试第1页 (pn=0)
    print("=== 测试第1页 (pn=0) ===")
    results_page1 = crawl_baidu_search(test_keyword, pn=0)
    print(f"Found {len(results_page1)} results for '{test_keyword}'")
    for i, result in enumerate(results_page1):
        print(f"\nResult {i+1}:")
        print(f"Title: {result['title']}")
        print(f"Summary: {result['summary']}")
    
    # 测试第2页 (pn=10)
    print("\n=== 测试第2页 (pn=10) ===")
    results_page2 = crawl_baidu_search(test_keyword, pn=10)
    print(f"Found {len(results_page2)} results for '{test_keyword}'")
    for i, result in enumerate(results_page2):
        print(f"\nResult {i+1}:")
        print(f"Title: {result['title']}")
        print(f"Summary: {result['summary']}")
    
    # 测试第4页 (pn=30) - 用户指定的参数
    print("\n=== 测试第4页 (pn=30) ===")
    results_page4 = crawl_baidu_search(test_keyword, pn=30)
    print(f"Found {len(results_page4)} results for '{test_keyword}'")
    for i, result in enumerate(results_page4):
        print(f"\nResult {i+1}:")
        print(f"Title: {result['title']}")
        print(f"Summary: {result['summary']}")
