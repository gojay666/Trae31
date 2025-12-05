import json
from datetime import datetime
from app import db
from app.models import CrawlerTask

# 用户提供的请求头信息
request_info_str = '''accept
text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
accept-encoding
gzip, deflate, br, zstd
accept-language
zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
cache-control
max-age=0
connection
keep-alive
cookie
nouse=nouse; costumerid=costumeridprifixgKCNaUwwk; costumeridprifixgKCNaUwwk=0; ValidateNumber="fNUBYncUEe8="
host
www.scpublic.cn
referer
https://www.scpublic.cn/
sec-ch-ua
"Chromium";v="142", "Microsoft Edge";v="142", "Not_A Brand";v="99"
sec-ch-ua-mobile
?0
sec-ch-ua-platform
"Windows"
sec-fetch-dest
document
sec-fetch-mode
navigate
sec-fetch-site
same-origin
sec-fetch-user
?1
upgrade-insecure-requests
1
user-agent
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0'''

def parse_request_info(request_str):
    """解析请求头信息为字典"""
    headers = {}
    lines = request_str.strip().split('\n')
    
    # 遍历所有行，两两配对组成键值对
    i = 0
    while i < len(lines):
        if i + 1 < len(lines):
            key = lines[i].strip()
            value = lines[i + 1].strip()
            headers[key] = value
            i += 2
        else:
            # 如果行数为奇数，处理最后一行
            key = lines[i].strip()
            headers[key] = ""
            i += 1
    
    return headers

def create_crawler_task(headers):
    """创建爬虫任务并保存到数据库"""
    # 从请求头中提取关键信息
    host = headers.get('host', '')
    url = headers.get('referer', '') if headers.get('referer', '') else f"https://{host}" if host else ''
    
    # 创建爬虫任务
    task = CrawlerTask(
        name=f"自动创建的任务 - {host}",
        description=f"从请求头自动生成的爬虫任务，目标站点：{host}",
        url=url,
        method="GET",
        headers=json.dumps(headers),
        params="",
        data="",
        rule=json.dumps({
            "title": {"selector": "h1"},
            "content": {"selector": "div.content"},
            "date": {"selector": ".date"}
        }),
        status="pending",
        interval=86400,  # 默认每天执行一次
        last_run_time=None,
        next_run_time=datetime.utcnow(),
        total_runs=0,
        success_runs=0,
        failed_runs=0
    )
    
    # 保存到数据库
    db.session.add(task)
    db.session.commit()
    
    return task

def main():
    """主函数"""
    # 解析请求头信息
    print("解析请求头信息...")
    headers = parse_request_info(request_info_str)
    print(f"解析完成，共{len(headers)}个请求头字段")
    
    # 打印解析结果
    print("\n解析结果：")
    for key, value in headers.items():
        print(f"  {key}: {value}")
    
    # 创建爬虫任务
    print("\n创建爬虫任务...")
    task = create_crawler_task(headers)
    print(f"爬虫任务创建成功！ID: {task.id}")
    print(f"  任务名称: {task.name}")
    print(f"  目标URL: {task.url}")
    print(f"  任务状态: {task.status}")
    print(f"  下次执行时间: {task.next_run_time}")

if __name__ == "__main__":
    # 初始化应用上下文
    from app import create_app
    app = create_app()
    
    with app.app_context():
        main()
