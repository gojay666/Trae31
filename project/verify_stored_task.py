import json
from app import create_app, db
from app.models import CrawlerTask

def verify_stored_task():
    """验证已存储的爬虫任务"""
    print("=== 验证爬虫任务存储结果 ===")
    
    # 获取所有爬虫任务
    tasks = CrawlerTask.query.all()
    print(f"\n数据库中共有 {len(tasks)} 个爬虫任务")
    
    if not tasks:
        print("\n没有找到任何爬虫任务！")
        return False
    
    # 按ID降序排序，显示最新的任务
    tasks.sort(key=lambda x: x.id, reverse=True)
    
    # 显示最新的5个任务
    print(f"\n最新的 {min(5, len(tasks))} 个任务：")
    for i, task in enumerate(tasks[:5]):
        print(f"\n任务 {i+1}:")
        print(f"  ID: {task.id}")
        print(f"  名称: {task.name}")
        print(f"  描述: {task.description}")
        print(f"  URL: {task.url}")
        print(f"  方法: {task.method}")
        print(f"  状态: {task.status}")
        print(f"  创建时间: {task.created_at}")
        
        # 解析请求头
        try:
            headers = json.loads(task.headers) if task.headers else {}
            print(f"  请求头数量: {len(headers)}")
            if headers:
                print("  主要请求头：")
                for key, value in list(headers.items())[:10]:  # 只显示前10个
                    print(f"    {key}: {value}")
                if len(headers) > 10:
                    print(f"    ... 还有 {len(headers) - 10} 个请求头")
        except Exception as e:
            print(f"  请求头解析失败: {e}")
    
    # 检查特定的任务（ID=1）
    print("\n=== 检查特定任务（ID=1）===\n")
    task = CrawlerTask.query.get(1)
    if task:
        print(f"找到任务 ID: {task.id}")
        print(f"任务名称: {task.name}")
        print(f"目标站点: {task.url}")
        
        # 检查请求头是否包含所有必要字段
        try:
            headers = json.loads(task.headers) if task.headers else {}
            
            # 检查用户提供的关键请求头是否存在
            key_headers = ['host', 'user-agent', 'accept', 'accept-encoding', 'accept-language']
            print("\n关键请求头检查：")
            for key in key_headers:
                if key in headers:
                    print(f"  ✓ {key}: {headers[key][:50]}{'...' if len(headers[key]) > 50 else ''}")
                else:
                    print(f"  ✗ {key}: 不存在")
            
            return True
            
        except Exception as e:
            print(f"\n✗ 请求头解析失败: {e}")
            return False
    else:
        print("✗ 没有找到ID为1的任务")
        return False

def main():
    """主函数"""
    app = create_app()
    
    with app.app_context():
        verify_stored_task()

if __name__ == "__main__":
    main()
