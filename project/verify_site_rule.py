import json
from app import create_app, db
from app.models import SiteRule

def verify_stored_rule():
    """验证已存储的站点规则"""
    print("=== 验证站点规则存储结果 ===")
    
    app = create_app()
    
    with app.app_context():
        # 获取所有站点规则
        rules = SiteRule.query.all()
        print(f"\n数据库中共有 {len(rules)} 个站点规则")
        
        if not rules:
            print("\n没有找到任何站点规则！")
            return False
        
        # 按ID降序排序，显示最新的规则
        rules.sort(key=lambda x: x.id, reverse=True)
        
        # 显示最新的5个规则
        print(f"\n最新的 {min(5, len(rules))} 个规则：")
        for i, rule in enumerate(rules[:5]):
            print(f"\n规则 {i+1}:")
            print(f"  ID: {rule.id}")
            print(f"  站点名称: {rule.site_name}")
            print(f"  站点URL: {rule.site_url}")
            print(f"  标题XPath: {rule.title_xpath}")
            print(f"  内容XPath: {rule.content_xpath}")
            print(f"  状态: {'启用' if rule.is_active else '禁用'}")
            print(f"  创建时间: {rule.created_at}")
            print(f"  更新时间: {rule.updated_at}")
            
            # 解析请求头
            try:
                headers = rule.get_request_headers()
                print(f"  请求头数量: {len(headers)}")
                if headers:
                    print("  主要请求头：")
                    for key, value in list(headers.items())[:10]:  # 只显示前10个
                        print(f"    {key}: {value}")
                    if len(headers) > 10:
                        print(f"    ... 还有 {len(headers) - 10} 个请求头")
            except Exception as e:
                print(f"  请求头解析失败: {e}")
        
        # 检查特定的规则（ID=1）
        print("\n=== 检查特定规则（ID=1）===\n")
        rule = SiteRule.query.get(1)
        if rule:
            print(f"找到规则 ID: {rule.id}")
            print(f"站点名称: {rule.site_name}")
            print(f"站点URL: {rule.site_url}")
            
            # 检查请求头是否包含所有必要字段
            try:
                headers = rule.get_request_headers()
                
                # 检查用户提供的关键请求头是否存在
                key_headers = ['host', 'user-agent', 'accept', 'accept-encoding', 'accept-language']
                print("\n关键请求头检查：")
                all_present = True
                for key in key_headers:
                    if key in headers:
                        print(f"  ✓ {key}: {headers[key][:50]}{'...' if len(headers[key]) > 50 else ''}")
                    else:
                        print(f"  ✗ {key}: 不存在")
                        all_present = False
                
                if all_present:
                    print("\n✓ 所有关键请求头都已正确存储！")
                    return True
                else:
                    print("\n✗ 部分关键请求头缺失！")
                    return False
                    
            except Exception as e:
                print(f"\n✗ 请求头解析失败: {e}")
                return False
        else:
            print("✗ 没有找到ID为1的规则")
            return False

def test_headers_usage():
    """测试请求头的实际使用"""
    print("\n=== 测试请求头的实际使用 ===")
    
    import requests
    
    app = create_app()
    
    with app.app_context():
        # 获取规则
        rule = SiteRule.query.get(1)
        if not rule:
            print("没有找到规则！")
            return False
        
        # 获取请求头
        headers = rule.get_request_headers()
        
        print(f"\n使用 {rule.site_name} 的请求头访问：{rule.site_url}")
        
        try:
            # 发送请求测试
            response = requests.get(rule.site_url, headers=headers, timeout=10)
            print(f"\n请求结果：")
            print(f"  状态码: {response.status_code}")
            print(f"  响应时间: {response.elapsed.total_seconds():.2f}秒")
            print(f"  内容长度: {len(response.text)}字节")
            
            if response.status_code == 200:
                print("\n✓ 请求成功！请求头可以正常使用。")
                return True
            else:
                print(f"\n✗ 请求失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"\n✗ 请求出错: {e}")
            return False

def main():
    """主函数"""
    # 验证存储结果
    verify_stored_rule()
    
    # 测试实际使用
    test_headers_usage()

if __name__ == "__main__":
    main()
