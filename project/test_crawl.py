import requests
import sys

# 测试数据采集功能是否返回正确数量的数据
def test_crawl_limit():
    base_url = "http://127.0.0.1:5000/api/crawl"
    test_keyword = "西昌"
    test_sources = ["baidu", "bing", "xinhua"]
    test_limits = [5, 10, 20]
    
    print(f"=== 测试数据采集功能返回数量一致性 ===\n")
    
    for source in test_sources:
        print(f"测试数据源: {source}")
        print("-" * 50)
        
        for limit in test_limits:
            print(f"  测试采集数量: {limit}")
            
            # 构造请求URL
            url = f"{base_url}?keyword={test_keyword}&source={source}&limit={limit}"
            
            try:
                # 发送请求
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                # 解析响应
                data = response.json()
                
                if data.get("success"):
                    returned_count = len(data.get("results", []))
                    print(f"    请求参数limit: {limit}")
                    print(f"    实际返回数量: {returned_count}")
                    print(f"    状态: {'✓ 通过' if returned_count == limit else '✗ 失败'}")
                else:
                    print(f"    错误: {data.get('message', '未知错误')}")
                    print(f"    状态: ✗ 失败")
                
            except requests.RequestException as e:
                print(f"    网络错误: {e}")
                print(f"    状态: ✗ 失败")
            except json.JSONDecodeError as e:
                print(f"    JSON解析错误: {e}")
                print(f"    状态: ✗ 失败")
            except Exception as e:
                print(f"    其他错误: {e}")
                print(f"    状态: ✗ 失败")
            
            print()
        
        print()

if __name__ == "__main__":
    import json
    test_crawl_limit()