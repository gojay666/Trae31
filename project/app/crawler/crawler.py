import requests
import urllib.parse
from bs4 import BeautifulSoup
import re
import uuid

class CrawlerConfig:
    """
    爬虫配置类，用于配置爬虫参数
    """
    def __init__(self, max_results=10, timeout=10, retries=3, user_agent=None):
        self.max_results = max_results
        self.timeout = timeout
        self.retries = retries
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0"

def crawl_baidu_search(keyword, page=0, config=None):
    """
    从百度搜索抓取指定关键字的结果（真实爬虫版本）
    
    Args:
        keyword: 搜索关键字
        page: 页码，默认为0代表第1页
        config: 爬虫配置对象
    
    Returns:
        list: 包含抓取结果的列表，每个结果包含标题、概要、封面、原始URL和来源
    """
    config = config or CrawlerConfig()
    
    # 计算pn参数（百度搜索结果的偏移量）
    pn = page * 10
    print(f"Crawling Baidu for keyword: {keyword}, page: {page}, pn: {pn}")
    
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
    
    # 优化请求头，提高反反爬能力
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'max-age=0',
        'connection': 'keep-alive',
        'host': 'www.baidu.com',
        'sec-ch-ua': '"Chromium";v="142", "Microsoft Edge";v="142", "Not_A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',  # 首次访问设置为none
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': config.user_agent,
        'referer': 'https://www.baidu.com/'  # 添加referer头
    }
    
    try:
        # 发送请求，让requests自动处理压缩的响应
        response = requests.get(base_url, params=params, headers=headers, timeout=config.timeout, 
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
        
        # 优化结果容器的查找方式
        print(f"HTML中包含的所有div数量: {len(soup.find_all('div'))}")
        
        # 方式1: 查找所有包含h3标签的div（百度搜索结果的常见结构）
        results_containers = []
        h3_tags = soup.find_all('h3')
        print(f"找到 {len(h3_tags)} 个h3标签")
        
        for h3 in h3_tags:
            parent_div = h3.find_parent('div')
            if parent_div:
                results_containers.append(parent_div)
        
        # 如果方式1没有找到结果，尝试方式2
        if not results_containers:
            print("使用方式2查找结果容器")
            results_containers = soup.find_all('div', class_=re.compile(r'result|c-container'))
        
        # 如果方式2也没有找到结果，尝试方式3
        if not results_containers:
            print("使用方式3查找结果容器")
            results_containers = soup.find_all('div', style=True)
        
        print(f"最终找到 {len(results_containers)} 个结果容器")
        
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
            # 尝试多种方式查找概要
            summary_selectors = [
                result.find('div', class_=re.compile(r'c-abstract|content|abstract')),
                result.find_next_sibling('div', class_=re.compile(r'c-abstract|content|abstract')),
                result.find('div', style=re.compile(r'display:inline')),
                result.find('span', class_=re.compile(r'c-abstract|content|abstract'))
            ]
            
            for selector in summary_selectors:
                if selector:
                    summary = selector.get_text(strip=True)
                    break
            
            # 尝试获取来源
            source = ''
            source_selectors = [
                result.find('span', class_=re.compile(r'c-color-gray|c-showurl|t'))
            ]
            
            for selector in source_selectors:
                if selector:
                    source = selector.get_text(strip=True)
                    break
            
            # 尝试获取封面（图片）
            cover = ''
            img_tag = result.find('img')
            if img_tag:
                cover = img_tag.get('src', '')
                if cover and not cover.startswith('http'):
                    cover = 'https://www.baidu.com' + cover
            
            # 将结果添加到列表
            results.append({
                'id': str(uuid.uuid4()),
                'title': title,
                'summary': summary,
                'cover': cover,
                'original_url': original_url,
                'source': source
            })
            print(f"成功添加一条结果: {title[:30]}...")
                
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
                    'id': str(uuid.uuid4()),
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
        
        # 返回所有结果，让上层函数决定返回多少条
        return final_results
        
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return []
    except Exception as e:
        print(f"处理响应失败: {e}")
        return []

def crawl_bing_search(keyword, page=0, config=None):
    """
    从Bing搜索抓取指定关键字的结果
    
    Args:
        keyword: 搜索关键字
        page: 页码，默认为0代表第1页
        config: 爬虫配置对象
    
    Returns:
        list: 包含抓取结果的列表，每个结果包含标题、概要、封面、原始URL和来源
    """
    config = config or CrawlerConfig()
    print(f"Crawling Bing for keyword: {keyword}, page: {page}")
    
    # 构建请求URL
    base_url = "https://www.bing.com/search"
    params = {
        'q': keyword,
        'first': page * config.max_results + 1  # Bing的页码参数
    }
    
    # 设置请求头
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'user-agent': config.user_agent
    }
    
    try:
        # 发送请求
        response = requests.get(base_url, params=params, headers=headers, timeout=config.timeout)
        response.raise_for_status()
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # 查找搜索结果
        result_containers = soup.find_all('li', class_='b_algo')
        
        for result in result_containers:
            # 获取标题
            h2_tag = result.find('h2')
            if not h2_tag:
                continue
            
            title = h2_tag.get_text(strip=True)
            
            # 获取链接
            link_tag = h2_tag.find('a')
            if not link_tag:
                continue
            
            original_url = link_tag.get('href', '')
            
            # 获取概要
            summary = ''
            summary_tag = result.find('div', class_='b_caption')
            if summary_tag:
                summary = summary_tag.get_text(strip=True)
            
            # 获取来源
            source = ''
            source_tag = result.find('cite')
            if source_tag:
                source = source_tag.get_text(strip=True)
            
            # 获取封面（图片）
            cover = ''
            img_tag = result.find('img')
            if img_tag:
                cover = img_tag.get('src', '')
                if cover and not cover.startswith('http'):
                    cover = 'https://www.bing.com' + cover
            
            results.append({
                'id': str(uuid.uuid4()),
                'title': title,
                'summary': summary,
                'cover': cover,
                'original_url': original_url,
                'source': source
            })
        
        print(f"成功抓取到 {len(results)} 条有效结果")
        return results
        
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return []
    except Exception as e:
        print(f"处理响应失败: {e}")
        return []

def crawl_xinhua_news(keyword='', page=0, limit=None, config=None):
    """
    爬取新华新闻四川要闻频道的新闻
    
    Args:
        keyword: 搜索关键词
        page: 页码，默认为0代表第1页
        limit: 每页返回结果数量
        config: 爬虫配置对象
    
    Returns:
        list: 包含抓取结果的列表，每个结果包含标题、概要、封面、原始URL和来源
    """
    config = config or CrawlerConfig()
    
    print(f"Crawling Xinhua News for keyword: {keyword}, page: {page}")
    
    # 构建请求URL
    base_url = "http://sc.news.cn/scyw.htm"
    
    # 优化请求头，提高反反爬能力
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'max-age=0',
        'connection': 'keep-alive',
        'host': 'sc.news.cn',
        'sec-ch-ua': '"Chromium";v="142", "Microsoft Edge";v="142", "Not_A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': config.user_agent
    }
    
    try:
        # 发送请求
        response = requests.get(base_url, headers=headers, timeout=config.timeout)
        response.raise_for_status()
        
        # 强制使用utf-8编码
        response.encoding = 'utf-8'
        html_text = response.text.encode('utf-8').decode('utf-8', 'ignore')
        
        # 解析HTML
        soup = BeautifulSoup(html_text, 'html.parser')
        results = []
        
        # 方式1: 直接查找所有包含新闻链接的a标签
        all_links = soup.find_all('a', href=True)
        
        # 遍历所有链接，提取新闻信息
        import re
        time_pattern = re.compile(r'(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})')
        
        for link in all_links:
            href = link.get('href')
            text = link.get_text(strip=True)
            
            # 过滤掉不相关的链接
            if not text or len(text) < 10:
                continue
                
            # 检查是否包含新闻.cn域名
            if 'news.cn' in href:
                # 查找标题中的时间戳
                time_match = time_pattern.search(text)
                
                if time_match:
                    timestamp = time_match.group(1)
                    title = time_pattern.sub('', text).strip()
                    
                    if title:
                        # 新华新闻没有摘要和封面，所以使用空字符串
                        summary = ''
                        cover = ''
                        source = '新华网'
                        
                        # 获取原始URL
                        original_url = href
                        if not original_url.startswith('http'):
                            original_url = 'https://www.news.cn' + original_url
                        
                        # 过滤与关键词相关的内容（如果提供了关键词）
                        if keyword and keyword not in title:
                            continue
                            
                        results.append({
                            'id': str(uuid.uuid4()),
                            'title': title,
                            'summary': summary,
                            'cover': cover,
                            'original_url': original_url,
                            'source': source
                        })
        
        # 如果没有找到结果，尝试方式2：查找所有包含时间戳的文本
        if not results:
            time_elements = soup.find_all(string=time_pattern)
            
            for elem in time_elements:
                # 查找包含这个时间戳的最近的a标签
                a_tag = elem.find_parents('a', href=True)
                if a_tag:
                    a_tag = a_tag[0]  # 取最近的一个a标签
                    href = a_tag.get('href')
                    full_link_text = a_tag.get_text(strip=True)
                    
                    time_match = time_pattern.search(full_link_text)
                    if time_match:
                        timestamp = time_match.group(1)
                        title = time_pattern.sub('', full_link_text).strip()
                        
                        if title:
                            summary = ''
                            cover = ''
                            source = '新华网'
                            original_url = href
                            
                            if not original_url.startswith('http'):
                                original_url = 'https://www.news.cn' + original_url
                            
                            # 过滤与关键词相关的内容（如果提供了关键词）
                            if keyword and keyword not in title:
                                continue
                            
                            results.append({
                                'id': str(uuid.uuid4()),
                                'title': title,
                                'summary': summary,
                                'cover': cover,
                                'original_url': original_url,
                                'source': source
                            })
        
        # 处理分页 - 确保页码从0开始
        if page < 0:
            page = 0
        
        # 使用config.max_results作为limit值，如果没有提供limit的话
        if limit is None and config:
            limit = config.max_results
        elif limit is None:
            limit = 10
            
        start = page * limit
        end = start + limit
        return results[start:end]
        
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return []
    except Exception as e:
        print(f"处理响应失败: {e}")
        return []

def crawl_data(keyword, source='baidu', page=1, limit=20, config=None):
    """
    统一的数据采集接口，支持多种数据源
    
    Args:
        keyword: 搜索关键字
        source: 数据源，支持 'baidu'、'bing' 和 'xinhua'
        page: 页码（1-based）
        limit: 最大返回结果数量
        config: 爬虫配置对象
    
    Returns:
        list: 包含抓取结果的列表
    """
    config = config or CrawlerConfig()
    
    # 转换为0-based页码
    actual_page = page - 1
    
    # 根据不同的数据源调用不同的爬取函数
    if source == 'baidu':
        # 百度搜索引擎的特殊处理（针对分页反爬）
        results = crawl_baidu_search(keyword, page=actual_page, config=config)
    elif source == 'bing':
        results = crawl_bing_search(keyword, page=actual_page, config=config)
    elif source == 'xinhua':
        results = crawl_xinhua_news(keyword, page=actual_page, limit=limit, config=config)
    else:
        results = []
    
    # 返回指定数量的结果
    return results[:limit]

def crawl_detailed_content(url, title_xpath=None, content_xpath=None, headers=None, config=None):
    """
    详细内容采集函数
    参数：
        url - 目标URL
        title_xpath - 标题XPATH（可选）
        content_xpath - 内容XPATH（可选）
        headers - 请求头（可选）
        config - 爬虫配置（可选）
    返回：解析后的详细内容
    """
    config = config or CrawlerConfig()
    
    try:
        # 构建请求头
        request_headers = {
            'user-agent': config.user_agent
        }
        
        if headers:
            request_headers.update(headers)
        
        # 发送请求
        response = requests.get(url, headers=request_headers, timeout=config.timeout)
        response.raise_for_status()
        
        # 强制使用utf-8编码
        response.encoding = 'utf-8'
        html_text = response.text.encode('utf-8').decode('utf-8', 'ignore')
        
        # 解析HTML
        soup = BeautifulSoup(html_text, 'html.parser')
        result = {}
        
        # 解析标题
        if title_xpath:
            title_element = soup.select_one(title_xpath)
            result['title'] = title_element.get_text(strip=True) if title_element else ''
        else:
            # 默认标题解析
            title = ''
            title_elements = soup.find_all(['h1', 'h2', 'h3'])
            if title_elements:
                title = title_elements[0].get_text(strip=True)
            result['title'] = title
        
        # 解析详细内容
        if content_xpath:
            content_element = soup.select_one(content_xpath)
            result['content'] = content_element.get_text(separator='\n', strip=True) if content_element else ''
        else:
            # 默认内容解析
            content = ''
            content_tags = soup.find_all(['article', 'div', 'section'], class_=lambda x: x and ('content' in x or 'article' in x or 'main' in x))
            if content_tags:
                for tag in content_tags:
                    if any(skip in tag.get('class', []) for skip in ['nav', 'sidebar', 'header', 'footer', 'comment']):
                        continue
                    content += tag.get_text(separator='\n', strip=True)
                    if len(content) > 1000:
                        break
            
            if not content or len(content) < 200:
                paragraphs = soup.find_all('p')
                content = '\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
            
            result['content'] = content
        
        # 提取图片
        images = []
        img_tags = soup.find_all('img', src=True)
        for img in img_tags:
            src = img.get('src', '')
            if src and len(src) > 5:
                if not src.startswith('http'):
                    if src.startswith('//'):
                        src = 'http:' + src
                    elif src.startswith('/'):
                        src = '/'.join(url.split('/')[:3]) + src
                images.append(src)
        result['images'] = list(set(images))  # 去重
        
        # 提取视频
        videos = []
        video_tags = soup.find_all(['video', 'iframe'], src=True)
        for video in video_tags:
            src = video.get('src', '')
            if src and ('video' in src or 'embed' in src):
                videos.append(src)
        result['videos'] = list(set(videos))  # 去重
        
        # 提取链接
        links = []
        a_tags = soup.find_all('a', href=True)
        for a in a_tags:
            href = a.get('href', '')
            text = a.get_text(strip=True)
            if href and len(href) > 5 and href != '#':
                if not href.startswith('http'):
                    if href.startswith('//'):
                        href = 'http:' + href
                    elif href.startswith('/'):
                        href = '/'.join(url.split('/')[:3]) + href
                links.append({'text': text, 'href': href})
        result['links'] = links
        
        # 提取元数据
        meta_data = {}
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name', '') or meta.get('property', '') or meta.get('http-equiv', '')
            content = meta.get('content', '')
            if name and content:
                meta_data[name] = content
        result['meta_data'] = meta_data
        
        return result
        
    except Exception as e:
        print(f"详细内容采集失败 {url}: {e}")
        return {
            'title': '',
            'content': '',
            'images': [],
            'videos': [],
            'links': [],
            'meta_data': {}
        }

if __name__ == "__main__":
    # 测试代码
    test_keyword = "西昌"  # 确保中文关键字正确编码
    
    # 测试百度搜索
    print("=== 测试百度搜索 ===")
    config = CrawlerConfig(max_results=5)
    results_baidu = crawl_data(test_keyword, source='baidu', page=1, config=config)
    print(f"Found {len(results_baidu)} results from Baidu")
    for i, result in enumerate(results_baidu):
        print(f"\nResult {i+1}:")
        print(f"Title: {result['title']}")
        print(f"Summary: {result['summary']}")
    
    # 测试Bing搜索
    print("\n=== 测试Bing搜索 ===")
    results_bing = crawl_data(test_keyword, source='bing', page=1, config=config)
    print(f"Found {len(results_bing)} results from Bing")
    for i, result in enumerate(results_bing):
        print(f"\nResult {i+1}:")
        print(f"Title: {result['title']}")
        print(f"Summary: {result['summary']}")
    
    # 测试新华新闻
    print("\n=== 测试新华新闻 ===")
    results_xinhua = crawl_data(test_keyword, source='xinhua', page=1, config=config)
    print(f"Found {len(results_xinhua)} results from Xinhua News")
    for i, result in enumerate(results_xinhua[:5]):
        print(f"\nResult {i+1}:")
        print(f"Title: {result['title']}")
        print(f"Original URL: {result['original_url']}")
        print(f"Source: {result['source']}")
    
    # 测试详细内容采集
    print("\n=== 测试详细内容采集 ===")
    if results_xinhua:
        test_url = results_xinhua[0]['original_url']
        detailed_content = crawl_detailed_content(test_url)
        print(f"\n详细内容采集结果：")
        print(f"标题: {detailed_content['title']}")
        print(f"内容长度: {len(detailed_content['content'])} 字符")
        print(f"图片数量: {len(detailed_content['images'])}")
        print(f"视频数量: {len(detailed_content['videos'])}")
        print(f"链接数量: {len(detailed_content['links'])}")
