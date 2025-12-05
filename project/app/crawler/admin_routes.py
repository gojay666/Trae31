from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for
from datetime import datetime
from flask_login import login_required, current_user
from app import db
from app.models import CrawlResult, DepthCrawlResult
from app.crawler.crawler import crawl_baidu_search, CrawlerConfig, crawl_data
import requests
from bs4 import BeautifulSoup
import json
import time

admin_crawler_bp = Blueprint('admin_crawler', __name__)


@admin_crawler_bp.route('/crawler', methods=['GET'])
def data_collection_page():
    """数据采集管理页面"""
    return render_template('crawler/admin/index.html')


@admin_crawler_bp.route('/api/crawl', methods=['POST'])
def api_crawl_data():
    """数据采集API接口"""
    try:
        keyword = request.form.get('keyword', '').strip()
        source = request.form.get('source', 'baidu').strip()  # 新增数据源参数
        if not keyword:
            return jsonify({'success': False, 'message': '请输入采集关键词'})
        
        # 验证数据源
        if source not in ['baidu', 'bing', 'xinhua']:
            return jsonify({'success': False, 'message': '不支持的数据源'})
        
        # 创建爬虫配置
        config = CrawlerConfig(max_results=10, timeout=15)
        
        # 执行采集
        results = crawl_data(keyword, source=source, page=1, config=config)
        
        # 保存到数据库临时表
        crawl_results = []
        for i, result in enumerate(results):
            # 模拟进度
            progress = int((i + 1) / len(results) * 100)
            
            # 保存到数据库
            crawl_result = CrawlResult(
                keyword=keyword,
                title=result.get('title', ''),
                summary=result.get('summary', ''),
                cover=result.get('cover', ''),
                original_url=result.get('original_url', ''),
                source=result.get('source', ''),
                raw_data=json.dumps(result, ensure_ascii=False)
            )
            db.session.add(crawl_result)
            db.session.commit()
            
            crawl_results.append({
                'id': crawl_result.id,
                'title': result.get('title', ''),
                'summary': result.get('summary', ''),
                'cover': result.get('cover', ''),
                'original_url': result.get('original_url', ''),
                'source': result.get('source', ''),
                'depth_crawled': False,
                'is_stored': False
            })
            
            # 模拟延迟，让用户看到进度
            time.sleep(0.2)
        
        return jsonify({
            'success': True,
            'message': '采集完成',
            'results': crawl_results,
            'total': len(crawl_results)
        })
        
    except Exception as e:
        current_app.logger.error(f"采集数据失败: {str(e)}")
        return jsonify({'success': False, 'message': f'采集失败: {str(e)}'})


@admin_crawler_bp.route('/api/depth_crawl', methods=['POST'])
def api_depth_crawl():
    """深度采集API接口"""
    try:
        # 处理单个深度采集请求
        result_id = request.form.get('result_id')
        # 处理批量深度采集请求
        ids = request.form.getlist('ids[]') or request.form.get('ids')
        
        # 确定要深度采集的结果ID列表
        if result_id:
            # 单个深度采集
            crawl_ids = [result_id]
        elif ids:
            # 批量深度采集
            if isinstance(ids, list):
                crawl_ids = ids
            else:
                # 如果是字符串形式的ID列表，进行解析
                crawl_ids = [id.strip() for id in ids.split(',') if id.strip().isdigit()]
        else:
            return jsonify({'success': False, 'message': '请选择要深度采集的内容'})
        
        # 执行深度采集
        def depth_crawl(url):
            """深度采集指定URL"""
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取正文内容
            content = ''
            content_tags = soup.find_all(['article', 'div', 'section'], class_=lambda x: x and ('content' in x or 'article' in x or 'main' in x))
            if content_tags:
                for tag in content_tags:
                    # 过滤掉导航、侧边栏等非正文内容
                    if any(skip in tag.get('class', []) for skip in ['nav', 'sidebar', 'header', 'footer', 'comment']):
                        continue
                    content += tag.get_text(separator='\n', strip=True)
                    if len(content) > 1000:
                        break
            
            # 如果没有找到合适的内容，尝试获取所有段落
            if not content or len(content) < 200:
                paragraphs = soup.find_all('p')
                content = '\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
            
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
            images = list(set(images))  # 去重
            
            # 提取视频
            videos = []
            video_tags = soup.find_all(['video', 'iframe'], src=True)
            for video in video_tags:
                src = video.get('src', '')
                if src and ('video' in src or 'embed' in src):
                    videos.append(src)
            videos = list(set(videos))  # 去重
            
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
            
            # 提取元数据
            meta_data = {}
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                name = meta.get('name', '') or meta.get('property', '') or meta.get('http-equiv', '')
                content = meta.get('content', '')
                if name and content:
                    meta_data[name] = content
            
            return {
                'content': content,
                'images': images,
                'videos': videos,
                'links': links,
                'meta_data': meta_data
            }
        
        # 初始化结果统计
        success_count = 0
        fail_count = 0
        
        # 循环处理每个要深度采集的ID
        for crawl_id in crawl_ids:
            try:
                # 获取要深度采集的结果
                crawl_result = CrawlResult.query.get(crawl_id)
                if not crawl_result:
                    fail_count += 1
                    continue
                
                # 检查是否已经深度采集
                if crawl_result.depth_crawled:
                    fail_count += 1
                    continue
                
                # 执行深度采集
                depth_data = depth_crawl(crawl_result.original_url)
                
                # 保存深度采集结果
                depth_result = DepthCrawlResult(
                    crawl_result_id=crawl_result.id,
                    content=depth_data.get('content', ''),
                    meta_data=json.dumps(depth_data.get('meta_data', {}), ensure_ascii=False)
                )
                depth_result.set_images(depth_data.get('images', []))
                depth_result.set_videos(depth_data.get('videos', []))
                depth_result.set_links(depth_data.get('links', []))
                
                db.session.add(depth_result)
                crawl_result.depth_crawled = True
                # 深度采集完成后，将数据加入仓库
                crawl_result.is_stored = True
                success_count += 1
                
            except Exception as e:
                current_app.logger.error(f"深度采集ID {crawl_id} 失败: {str(e)}")
                fail_count += 1
        
        # 提交所有更改
        db.session.commit()
        
        # 返回结果
        if len(crawl_ids) == 1:
            # 单个深度采集的返回格式
            if success_count == 1:
                return jsonify({
                    'success': True,
                    'message': '深度采集完成'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '深度采集失败'
                })
        else:
            # 批量深度采集的返回格式
            return jsonify({
                'success': True,
                'message': '批量深度采集完成',
                'data': {
                    'total': len(crawl_ids),
                    'success_count': success_count,
                    'fail_count': fail_count
                }
            })
        
    except Exception as e:
        current_app.logger.error(f"深度采集失败: {str(e)}")
        return jsonify({'success': False, 'message': f'深度采集失败: {str(e)}'})


@admin_crawler_bp.route('/api/store_data', methods=['POST'])
def api_store_data():
    """存储数据到数据库"""
    try:
        result_ids = request.form.get('result_ids', '')
        if not result_ids:
            return jsonify({'success': False, 'message': '请选择要存储的数据'})
        
        # 解析结果ID列表
        result_ids = [int(id.strip()) for id in result_ids.split(',') if id.strip().isdigit()]
        
        # 更新存储状态
        updated_count = 0
        stored_count = 0
        for result_id in result_ids:
            crawl_result = CrawlResult.query.get(result_id)
            if crawl_result:
                if crawl_result.is_stored:
                    # 数据已存在，更新数据
                    # 这里可以根据需要添加更多的更新逻辑
                    crawl_result.updated_at = datetime.utcnow()
                    stored_count += 1
                else:
                    # 数据不存在，标记为已存储
                    crawl_result.is_stored = True
                    updated_count += 1
        
        db.session.commit()
        
        message = ''
        if updated_count > 0:
            message += f'成功存储{updated_count}条数据'
        if stored_count > 0:
            if message:
                message += f'，{stored_count}条数据已存在并已更新'
            else:
                message += f'{stored_count}条数据已存在并已更新'
        
        return jsonify({
            'success': True,
            'message': message or '没有数据需要存储',
            'updated_count': updated_count,
            'stored_count': stored_count
        })
        
    except Exception as e:
        current_app.logger.error(f"存储数据失败: {str(e)}")
        return jsonify({'success': False, 'message': f'存储数据失败: {str(e)}'})


@admin_crawler_bp.route('/api/crawl_results', methods=['GET'])
def api_crawl_results():
    """获取采集结果列表"""
    try:
        keyword = request.args.get('keyword', '').strip()
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        # 构建查询
        query = CrawlResult.query
        if keyword:
            query = query.filter(CrawlResult.keyword.like(f'%{keyword}%') | CrawlResult.title.like(f'%{keyword}%'))
        
        # 分页查询
        total = query.count()
        offset = (page - 1) * limit
        results = query.order_by(CrawlResult.created_at.desc()).offset(offset).limit(limit).all()
        
        # 转换为JSON格式
        data = []
        for result in results:
            data.append({
                'id': result.id,
                'keyword': result.keyword,
                'title': result.title,
                'summary': result.summary,
                'cover': result.cover,
                'original_url': result.original_url,
                'source': result.source,
                'depth_crawled': result.depth_crawled,
                'is_stored': result.is_stored,
                'created_at': result.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'code': 0,
            'msg': '',
            'count': total,
            'data': data
        })
        
    except Exception as e:
        current_app.logger.error(f"获取采集结果失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取采集结果失败: {str(e)}'})


@admin_crawler_bp.route('/api/delete_result', methods=['POST'])
def api_delete_result():
    """删除采集结果"""
    try:
        result_id = request.form.get('result_id', '')
        if not result_id:
            return jsonify({'success': False, 'message': '请选择要删除的数据'})
        
        # 删除关联的深度采集结果
        DepthCrawlResult.query.filter_by(crawl_result_id=result_id).delete()
        
        # 删除采集结果
        CrawlResult.query.filter_by(id=result_id).delete()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': '删除成功'})
        
    except Exception as e:
        current_app.logger.error(f"删除采集结果失败: {str(e)}")
        return jsonify({'success': False, 'message': f'删除采集结果失败: {str(e)}'})


@admin_crawler_bp.route('/api/delete_selected', methods=['POST'])
def api_delete_selected():
    """批量删除采集结果"""
    try:
        result_ids = request.form.get('result_ids', '')
        if not result_ids:
            return jsonify({'success': False, 'message': '请选择要删除的数据'})
        
        # 解析结果ID列表
        result_ids = [int(id.strip()) for id in result_ids.split(',') if id.strip().isdigit()]
        
        # 删除关联的深度采集结果
        DepthCrawlResult.query.filter(DepthCrawlResult.crawl_result_id.in_(result_ids)).delete()
        
        # 删除采集结果
        CrawlResult.query.filter(CrawlResult.id.in_(result_ids)).delete()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'成功删除{len(result_ids)}条数据',
            'deleted_count': len(result_ids)
        })
        
    except Exception as e:
        current_app.logger.error(f"批量删除失败: {str(e)}")
        return jsonify({'success': False, 'message': f'批量删除失败: {str(e)}'})

@admin_crawler_bp.route('/api/stats', methods=['GET'])
def api_get_stats():
    """获取采集统计数据"""
    try:
        from datetime import datetime, timedelta
        
        # 计算时间范围（最近7天）
        today = datetime.utcnow().date()
        seven_days_ago = today - timedelta(days=7)
        
        # 总采集数量
        total_count = CrawlResult.query.count()
        
        # 已深度采集数量
        depth_crawled_count = CrawlResult.query.filter_by(depth_crawled=True).count()
        
        # 已存储数量
        stored_count = CrawlResult.query.filter_by(is_stored=True).count()
        
        # 按关键词统计
        keywords_stats = db.session.query(
            CrawlResult.keyword,
            db.func.count(CrawlResult.id).label('count')
        ).group_by(CrawlResult.keyword).order_by(db.func.count(CrawlResult.id).desc()).limit(10).all()
        
        # 按日期统计（最近7天）
        date_stats = []
        for i in range(7):
            date = seven_days_ago + timedelta(days=i)
            next_date = date + timedelta(days=1)
            count = CrawlResult.query.filter(
                CrawlResult.created_at >= datetime.combine(date, datetime.min.time()),
                CrawlResult.created_at < datetime.combine(next_date, datetime.min.time())
            ).count()
            date_stats.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': count
            })
        
        return jsonify({
            'success': True,
            'data': {
                'total_count': total_count,
                'depth_crawled_count': depth_crawled_count,
                'stored_count': stored_count,
                'keywords_stats': [{'keyword': item.keyword, 'count': item.count} for item in keywords_stats],
                'date_stats': date_stats
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"获取统计数据失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取统计数据失败: {str(e)}'})


# 采集规则库路由
@admin_crawler_bp.route('/rules', methods=['GET'])
def rules_page():
    """采集规则库页面"""
    return render_template('crawler/admin/rules.html')


@admin_crawler_bp.route('/api/rules', methods=['GET'])
def api_get_rules():
    """获取采集规则列表"""
    try:
        from app.models import SiteRule
        
        keyword = request.args.get('keyword', '').strip()
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        # 构建查询
        query = SiteRule.query
        if keyword:
            query = query.filter(SiteRule.site_name.like(f'%{keyword}%') | SiteRule.site_url.like(f'%{keyword}%'))
        
        # 分页查询
        total = query.count()
        offset = (page - 1) * limit
        rules = query.order_by(SiteRule.created_at.desc()).offset(offset).limit(limit).all()
        
        # 转换为JSON格式
        data = []
        for rule in rules:
            data.append({
                'id': rule.id,
                'site_name': rule.site_name,
                'site_url': rule.site_url,
                'title_xpath': rule.title_xpath,
                'content_xpath': rule.content_xpath,
                'request_headers': rule.get_request_headers(),
                'is_active': rule.is_active,
                'created_at': rule.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'code': 0,
            'msg': '',
            'count': total,
            'data': data
        })
        
    except Exception as e:
        current_app.logger.error(f"获取规则列表失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取规则列表失败: {str(e)}'})


def parse_request_headers(headers_str):
    """解析请求头字符串，支持原始格式和JSON格式
    
    原始格式示例：
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif
    
    JSON格式示例：
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "text/html"}
    """
    import json
    
    if not headers_str:
        return {}
    
    # 尝试解析为JSON
    try:
        return json.loads(headers_str)
    except json.JSONDecodeError:
        # 如果不是JSON格式，尝试解析为原始请求头格式
        headers = {}
        lines = headers_str.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()
        return headers

@admin_crawler_bp.route('/api/rules', methods=['POST'])
def api_add_rule():
    """新增采集规则"""
    try:
        from app.models import SiteRule
        import json
        
        site_name = request.form.get('site_name', '').strip()
        site_url = request.form.get('site_url', '').strip()
        title_xpath = request.form.get('title_xpath', '').strip()
        content_xpath = request.form.get('content_xpath', '').strip()
        request_headers = request.form.get('request_headers', '').strip()
        is_active = request.form.get('is_active', '1') == '1'
        
        # 验证参数
        if not site_name:
            return jsonify({'success': False, 'message': '请输入站点名称'})
        if not site_url:
            return jsonify({'success': False, 'message': '请输入站点URL'})
        if not title_xpath:
            return jsonify({'success': False, 'message': '请输入标题XPATH'})
        if not content_xpath:
            return jsonify({'success': False, 'message': '请输入详细内容XPATH'})
        
        # 检查站点名称是否已存在
        existing_rule = SiteRule.query.filter_by(site_name=site_name).first()
        if existing_rule:
            return jsonify({'success': False, 'message': '站点名称已存在'})
        
        # 创建规则
        rule = SiteRule(
            site_name=site_name,
            site_url=site_url,
            title_xpath=title_xpath,
            content_xpath=content_xpath,
            is_active=is_active
        )
        
        # 设置请求头
        if request_headers:
            try:
                headers = parse_request_headers(request_headers)
                rule.set_request_headers(headers)
            except Exception as e:
                return jsonify({'success': False, 'message': f'请求头解析错误: {str(e)}'})
        
        db.session.add(rule)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '规则创建成功',
            'rule': {
                'id': rule.id,
                'site_name': rule.site_name,
                'site_url': rule.site_url,
                'title_xpath': rule.title_xpath,
                'content_xpath': rule.content_xpath,
                'request_headers': rule.get_request_headers(),
                'is_active': rule.is_active
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"创建规则失败: {str(e)}")
        return jsonify({'success': False, 'message': f'创建规则失败: {str(e)}'})


@admin_crawler_bp.route('/api/rules/<int:rule_id>', methods=['PUT'])
def api_update_rule(rule_id):
    """更新采集规则"""
    try:
        from app.models import SiteRule
        import json
        
        # 获取规则
        rule = SiteRule.query.get(rule_id)
        if not rule:
            return jsonify({'success': False, 'message': '规则不存在'})
        
        # 获取参数
        site_name = request.form.get('site_name', '').strip()
        site_url = request.form.get('site_url', '').strip()
        title_xpath = request.form.get('title_xpath', '').strip()
        content_xpath = request.form.get('content_xpath', '').strip()
        request_headers = request.form.get('request_headers', '').strip()
        is_active = request.form.get('is_active', '1') == '1'
        
        # 验证参数
        if not site_name:
            return jsonify({'success': False, 'message': '请输入站点名称'})
        if not site_url:
            return jsonify({'success': False, 'message': '请输入站点URL'})
        if not title_xpath:
            return jsonify({'success': False, 'message': '请输入标题XPATH'})
        if not content_xpath:
            return jsonify({'success': False, 'message': '请输入详细内容XPATH'})
        
        # 检查站点名称是否已存在（排除当前规则）
        existing_rule = SiteRule.query.filter_by(site_name=site_name).filter(SiteRule.id != rule_id).first()
        if existing_rule:
            return jsonify({'success': False, 'message': '站点名称已存在'})
        
        # 更新规则
        rule.site_name = site_name
        rule.site_url = site_url
        rule.title_xpath = title_xpath
        rule.content_xpath = content_xpath
        rule.is_active = is_active
        
        # 设置请求头
        if request_headers:
            try:
                headers = parse_request_headers(request_headers)
                rule.set_request_headers(headers)
            except Exception as e:
                return jsonify({'success': False, 'message': f'请求头解析错误: {str(e)}'})
        else:
            rule.request_headers = None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '规则更新成功',
            'rule': {
                'id': rule.id,
                'site_name': rule.site_name,
                'site_url': rule.site_url,
                'title_xpath': rule.title_xpath,
                'content_xpath': rule.content_xpath,
                'request_headers': rule.get_request_headers(),
                'is_active': rule.is_active
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"更新规则失败: {str(e)}")
        return jsonify({'success': False, 'message': f'更新规则失败: {str(e)}'})


@admin_crawler_bp.route('/api/rules/<int:rule_id>', methods=['DELETE'])
def api_delete_rule(rule_id):
    """删除采集规则"""
    try:
        from app.models import SiteRule
        
        # 获取规则
        rule = SiteRule.query.get(rule_id)
        if not rule:
            return jsonify({'success': False, 'message': '规则不存在'})
        
        # 删除规则
        db.session.delete(rule)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '规则删除成功'
        })
        
    except Exception as e:
        current_app.logger.error(f"删除规则失败: {str(e)}")
        return jsonify({'success': False, 'message': f'删除规则失败: {str(e)}'})
