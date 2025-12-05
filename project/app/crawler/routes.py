from flask import Blueprint, request, jsonify
from app.crawler.crawler import crawl_data

# 创建蓝图
crawler_bp = Blueprint('crawler', __name__)

@crawler_bp.route('/api/crawl', methods=['GET'])
def crawl_data_api():
    """
    数据采集API接口
    参数：
        keyword - 搜索关键字
        source - 数据源，支持 'baidu'、'bing' 和 'xinhua'，默认为 'baidu'
        pn - 翻页参数，默认为0代表第1页，10代表第2页，20代表第3页，以此类推
    返回：JSON格式的搜索结果
    """
    try:
        # 获取搜索关键字
        keyword = request.args.get('keyword', '')
        
        # 获取数据源参数，默认为 'baidu'
        source = request.args.get('source', 'baidu')
        
        # 获取采集数量参数，默认为20
        limit = request.args.get('limit', 20)
        try:
            limit = int(limit)
        except ValueError:
            limit = 20
        
        # 限制最大采集数量为100
        limit = min(max(limit, 1), 100)
        
        if not keyword:
            return jsonify({
                'success': False,
                'message': 'Missing keyword parameter'
            }), 400
        
        # 调用抓取函数，支持多页抓取直到达到指定数量
        all_results = []
        page = 0
        max_attempts = 5  # 最多尝试抓取的页数
        
        while len(all_results) < limit and page < max_attempts:
            # 计算还需要多少结果
            remaining = limit - len(all_results)
            
            # 抓取当前页
            page_results = crawl_data(keyword, source=source, page=page, limit=remaining)
            
            # 如果当前页没有结果，停止抓取
            if not page_results:
                break
            
            # 将当前页结果添加到总结果中
            all_results.extend(page_results)
            
            # 增加页码
            page += 1
        
        # 只返回用户指定数量的结果
        final_results = all_results[:limit]
        
        return jsonify({
            'success': True,
            'keyword': keyword,
            'source': source,
            'limit': limit,
            'count': len(final_results),
            'results': final_results
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500



