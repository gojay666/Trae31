from app.crawler.crawler import crawl_xinhua_news, crawl_data

# 测试1: 无关键词抓取
try:
    print("=== 测试1: 无关键词抓取 ===")
    results1 = crawl_xinhua_news(keyword="", page=0, limit=10)
    print(f"无关键词时找到 {len(results1)} 条结果")
    
    for i, result in enumerate(results1[:5]):
        print(f"\n结果 {i+1}:")
        print(f"标题: {result['title']}")
        print(f"原始URL: {result['original_url']}")
        print(f"来源: {result['source']}")
        print(f"摘要: {result['summary']}")
        print(f"封面: {result['cover']}")
except Exception as e:
    print(f"测试1失败: {e}")

# 测试2: 通过统一接口抓取
try:
    print("\n=== 测试2: 通过统一接口抓取 ===")
    results2 = crawl_data(keyword="", source='xinhua', page=1, limit=5)
    print(f"统一接口无关键词时找到 {len(results2)} 条结果")
    
    for i, result in enumerate(results2[:5]):
        print(f"\n结果 {i+1}:")
        print(f"标题: {result['title']}")
        print(f"原始URL: {result['original_url']}")
        print(f"来源: {result['source']}")
except Exception as e:
    print(f"测试2失败: {e}")

# 测试3: 有关键词抓取（可能没有结果，这是正常的）
try:
    print("\n=== 测试3: 有关键词抓取 ===")
    results3 = crawl_xinhua_news(keyword="四川", page=0, limit=5)
    print(f"关键词'四川'时找到 {len(results3)} 条结果")
    
    for i, result in enumerate(results3[:3]):
        print(f"\n结果 {i+1}:")
        print(f"标题: {result['title']}")
        print(f"原始URL: {result['original_url']}")
except Exception as e:
    print(f"测试3失败: {e}")
