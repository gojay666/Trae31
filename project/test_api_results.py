import requests
import json

def test_api_crawl_results():
    """测试API返回的结果是否包含唯一ID"""
    base_url = "http://127.0.0.1:5000/api/crawl"
    test_keyword = "西昌"
    test_sources = ["baidu", "bing"]
    limit = 5
    
    print("=== 测试API返回结果的ID唯一性 ===")
    
    for source in test_sources:
        print(f"\n测试数据源: {source}")
        print("-" * 40)
        
        url = f"{base_url}?keyword={test_keyword}&source={source}&limit={limit}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("success"):
                results = data.get("results", [])
                print(f"返回结果数量: {len(results)}")
                
                # 检查ID是否存在且唯一
                ids = []
                for i, result in enumerate(results):
                    result_id = result.get("id")
                    print(f"  结果 {i+1}: ID={result_id}, 标题={result.get('title')[:20]}...")
                    
                    if not result_id:
                        print(f"    错误: 结果 {i+1} 没有ID")
                    elif result_id in ids:
                        print(f"    错误: 结果 {i+1} 的ID重复")
                    else:
                        ids.append(result_id)
                
                if len(ids) == len(results) and len(set(ids)) == len(ids):
                    print("\n✓ 所有结果都有唯一ID")
                else:
                    print("\n✗ 部分结果没有ID或ID重复")
            else:
                print(f"API请求失败: {data.get('message', '未知错误')}")
                
        except requests.RequestException as e:
            print(f"网络请求失败: {e}")
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")

if __name__ == "__main__":
    test_api_crawl_results()
