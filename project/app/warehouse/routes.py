from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import CrawlResult, DepthCrawlResult
import json
import time

# 创建蓝图
warehouse_bp = Blueprint('warehouse', __name__)

@warehouse_bp.route('/warehouse', methods=['GET'])
def warehouse_page():
    """数据仓库管理页面"""
    return render_template('warehouse/admin/index.html')

@warehouse_bp.route('/api/warehouse/data', methods=['GET'])
def get_warehouse_data():
    """
    获取数据仓库中的数据列表
    参数：
        page - 页码，默认1
        limit - 每页数量，默认10
        keyword - 搜索关键词
        source - 数据源筛选
    返回：JSON格式的数据列表
    """
    try:
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        keyword = request.args.get('keyword', '')
        source = request.args.get('source', '')
        
        # 计算偏移量
        offset = (page - 1) * limit
        
        # 构建查询
        query = CrawlResult.query
        
        # 关键词搜索
        if keyword:
            query = query.filter(
                CrawlResult.keyword.like(f'%{keyword}%') | 
                CrawlResult.title.like(f'%{keyword}%') |
                CrawlResult.summary.like(f'%{keyword}%')
            )
        
        # 数据源筛选
        if source:
            query = query.filter(CrawlResult.source == source)
        
        # 执行查询
        total_count = query.count()
        results = query.order_by(CrawlResult.created_at.desc()).offset(offset).limit(limit).all()
        
        # 格式化结果
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
                'created_at': result.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': result.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'success': True,
            'total': total_count,
            'data': data,
            'page': page,
            'limit': limit
        })
        
    except Exception as e:
        current_app.logger.error(f"获取数据仓库数据失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取数据失败: {str(e)}'})

@warehouse_bp.route('/api/warehouse/data/<int:data_id>', methods=['GET'])
def get_warehouse_data_detail(data_id):
    """
    获取数据仓库中指定ID的数据详情
    参数：
        data_id - 数据ID
    返回：JSON格式的数据详情
    """
    try:
        # 查询数据
        result = CrawlResult.query.get(data_id)
        if not result:
            return jsonify({'success': False, 'message': '数据不存在'})
        
        # 查询深度采集数据
        depth_result = DepthCrawlResult.query.filter_by(crawl_result_id=data_id).first()
        
        # 格式化结果
        data = {
            'id': result.id,
            'keyword': result.keyword,
            'title': result.title,
            'summary': result.summary,
            'cover': result.cover,
            'original_url': result.original_url,
            'source': result.source,
            'depth_crawled': result.depth_crawled,
            'is_stored': result.is_stored,
            'raw_data': result.raw_data,
            'created_at': result.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': result.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'depth_data': {
                'content': depth_result.content if depth_result else '',
                'images': depth_result.get_images() if depth_result else [],
                'videos': depth_result.get_videos() if depth_result else [],
                'links': depth_result.get_links() if depth_result else [],
                'meta_data': depth_result.get_meta_data() if depth_result else {}
            } if depth_result else None
        }
        
        return jsonify({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        current_app.logger.error(f"获取数据详情失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取数据详情失败: {str(e)}'})

@warehouse_bp.route('/api/warehouse/data/<int:data_id>', methods=['PUT'])
def update_warehouse_data(data_id):
    """
    更新数据仓库中的数据
    参数：
        data_id - 数据ID
        表单数据：title, summary, source等
    返回：JSON格式的更新结果
    """
    try:
        # 查询数据
        result = CrawlResult.query.get(data_id)
        if not result:
            return jsonify({'success': False, 'message': '数据不存在'})
        
        # 获取更新数据
        title = request.form.get('title', result.title)
        summary = request.form.get('summary', result.summary)
        source = request.form.get('source', result.source)
        cover = request.form.get('cover', result.cover)
        
        # 更新数据
        result.title = title
        result.summary = summary
        result.source = source
        result.cover = cover
        
        # 提交更新
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '数据更新成功'
        })
        
    except Exception as e:
        current_app.logger.error(f"更新数据失败: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新数据失败: {str(e)}'})

@warehouse_bp.route('/api/warehouse/data/<int:data_id>', methods=['DELETE'])
def delete_warehouse_data(data_id):
    """
    删除数据仓库中的数据
    参数：
        data_id - 数据ID
    返回：JSON格式的删除结果
    """
    try:
        # 先删除深度采集数据
        DepthCrawlResult.query.filter_by(crawl_result_id=data_id).delete()
        
        # 再删除采集结果数据
        result = CrawlResult.query.get(data_id)
        if not result:
            return jsonify({'success': False, 'message': '数据不存在'})
        
        db.session.delete(result)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '数据删除成功'
        })
        
    except Exception as e:
        current_app.logger.error(f"删除数据失败: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除数据失败: {str(e)}'})

@warehouse_bp.route('/api/warehouse/batch_delete', methods=['POST'])
def batch_delete_warehouse_data():
    """
    批量删除数据仓库中的数据
    参数：
        result_ids - 数据ID列表（JSON格式）
    返回：JSON格式的删除结果
    """
    try:
        # 获取要删除的数据ID列表
        result_ids = request.form.get('result_ids')
        if not result_ids:
            return jsonify({'success': False, 'message': '请选择要删除的数据'})
        
        try:
            result_ids = json.loads(result_ids)
        except json.JSONDecodeError:
            return jsonify({'success': False, 'message': '数据格式错误'})
        
        if not isinstance(result_ids, list) or len(result_ids) == 0:
            return jsonify({'success': False, 'message': '请选择要删除的数据'})
        
        # 先删除深度采集数据
        DepthCrawlResult.query.filter(DepthCrawlResult.crawl_result_id.in_(result_ids)).delete()
        
        # 再删除采集结果数据
        CrawlResult.query.filter(CrawlResult.id.in_(result_ids)).delete()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'成功删除 {len(result_ids)} 条数据'
        })
        
    except Exception as e:
        current_app.logger.error(f"批量删除数据失败: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'批量删除数据失败: {str(e)}'})


@warehouse_bp.route('/api/warehouse/detailed_crawl/<int:data_id>', methods=['POST'])
def detailed_crawl_data(data_id):
    """
    详细内容采集API接口（单个数据）
    参数：
        data_id - 数据ID
    返回：JSON格式的采集结果
    """
    try:
        from app.models import SiteRule
        from app.crawler.crawler import crawl_detailed_content
        
        # 获取要采集的结果
        crawl_result = CrawlResult.query.get(data_id)
        if not crawl_result:
            return jsonify({'success': False, 'message': '数据不存在'})
        
        # 根据来源匹配规则
        site_rule = SiteRule.query.filter(
            SiteRule.is_active == True,
            SiteRule.site_name == crawl_result.source
        ).first()
        
        # 执行详细内容采集
        if site_rule:
            # 使用匹配的规则进行采集
            detailed_content = crawl_detailed_content(
                crawl_result.original_url,
                title_xpath=site_rule.title_xpath,
                content_xpath=site_rule.content_xpath,
                headers=site_rule.get_request_headers()
            )
        else:
            # 没有匹配的规则，使用默认采集
            detailed_content = crawl_detailed_content(crawl_result.original_url)
        
        # 检查是否需要更新规则
        if site_rule and (not detailed_content.get('title') or not detailed_content.get('content')):
            # 尝试自动更新规则
            updated = update_crawl_rules(
                crawl_result.original_url,
                site_rule,
                crawl_result.title
            )
            if updated:
                # 使用更新后的规则重新采集
                detailed_content = crawl_detailed_content(
                    crawl_result.original_url,
                    title_xpath=site_rule.title_xpath,
                    content_xpath=site_rule.content_xpath,
                    headers=site_rule.get_request_headers()
                )
        
        # 保存详细采集结果
        depth_result = DepthCrawlResult.query.filter_by(crawl_result_id=data_id).first()
        if depth_result:
            # 更新已有结果
            depth_result.content = detailed_content.get('content', '')
            depth_result.set_images(detailed_content.get('images', []))
            depth_result.set_videos(detailed_content.get('videos', []))
            depth_result.set_links(detailed_content.get('links', []))
            depth_result.set_meta_data(detailed_content.get('meta_data', {}))
        else:
            # 创建新结果
            depth_result = DepthCrawlResult(
                crawl_result_id=data_id,
                content=detailed_content.get('content', ''),
                meta_data=json.dumps(detailed_content.get('meta_data', {}), ensure_ascii=False)
            )
            depth_result.set_images(detailed_content.get('images', []))
            depth_result.set_videos(detailed_content.get('videos', []))
            depth_result.set_links(detailed_content.get('links', []))
            db.session.add(depth_result)
        
        # 更新采集状态
        crawl_result.depth_crawled = True
        crawl_result.is_stored = True
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '详细内容采集完成',
            'data': detailed_content
        })
        
    except Exception as e:
        current_app.logger.error(f"详细内容采集失败: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'详细内容采集失败: {str(e)}'})





def update_crawl_rules(url, site_rule, expected_title):
    """
    自动更新采集规则
    参数：
        url - 目标URL
        site_rule - 现有规则对象
        expected_title - 期望的标题
    返回：是否更新成功
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # 发送请求
        headers = site_rule.get_request_headers()
        if not headers:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        updated = False
        
        # 尝试更新标题XPATH
        if not site_rule.title_xpath or not soup.select_one(site_rule.title_xpath):
            # 查找可能的标题元素
            title_elements = soup.find_all(['h1', 'h2', 'h3'])
            for title_element in title_elements:
                title_text = title_element.get_text(strip=True)
                if expected_title in title_text or title_text in expected_title:
                    # 获取XPATH
                    new_title_xpath = get_element_xpath(title_element)
                    if new_title_xpath:
                        site_rule.title_xpath = new_title_xpath
                        updated = True
                        break
        
        # 尝试更新内容XPATH
        if not site_rule.content_xpath or not soup.select_one(site_rule.content_xpath):
            # 查找可能的内容元素
            content_elements = soup.find_all(['article', 'div', 'section'])
            for content_element in content_elements:
                if any(skip in content_element.get('class', []) for skip in ['nav', 'sidebar', 'header', 'footer', 'comment']):
                    continue
                
                content_text = content_element.get_text(separator='\n', strip=True)
                if len(content_text) > 500:
                    # 获取XPATH
                    new_content_xpath = get_element_xpath(content_element)
                    if new_content_xpath:
                        site_rule.content_xpath = new_content_xpath
                        updated = True
                        break
        
        if updated:
            db.session.commit()
        
        return updated
        
    except Exception as e:
        current_app.logger.error(f"更新采集规则失败 {url}: {str(e)}")
        return False


def get_element_xpath(element):
    """
    获取元素的XPATH路径
    参数：
        element - BeautifulSoup元素对象
    返回：XPATH字符串
    """
    try:
        components = []
        child = element
        while child.parent:
            siblings = child.parent.find_all(child.name, recursive=False)
            if len(siblings) > 1:
                components.append(f"{child.name}[{siblings.index(child)+1}]")
            else:
                components.append(child.name)
            child = child.parent
        components.reverse()
        return '/' + '/'.join(components)
    except Exception as e:
        current_app.logger.error(f"获取元素XPATH失败: {str(e)}")
        return ''


@warehouse_bp.route('/api/warehouse/batch_detailed_crawl', methods=['POST'])
def batch_detailed_crawl_data():
    """
    批量详细内容采集API接口
    参数：
        data_ids - 数据ID列表（JSON格式）
    返回：JSON格式的采集结果
    """
    try:
        # 获取要采集的数据ID列表
        data_ids = request.form.get('data_ids')
        if not data_ids:
            return jsonify({'success': False, 'message': '请选择要采集的数据'})
        
        try:
            data_ids = json.loads(data_ids)
        except json.JSONDecodeError:
            return jsonify({'success': False, 'message': '数据格式错误'})
        
        if not isinstance(data_ids, list) or len(data_ids) == 0:
            return jsonify({'success': False, 'message': '请选择要采集的数据'})
        
        # 初始化结果统计
        success_count = 0
        fail_count = 0
        
        # 循环处理每个要采集的ID
        for data_id in data_ids:
            try:
                # 获取要采集的结果
                crawl_result = CrawlResult.query.get(data_id)
                if not crawl_result:
                    fail_count += 1
                    continue
                
                # 调用单个采集函数
                from app.models import SiteRule
                from app.crawler.crawler import crawl_detailed_content
                
                # 根据来源匹配规则
                site_rule = SiteRule.query.filter(
                    SiteRule.is_active == True,
                    SiteRule.site_name == crawl_result.source
                ).first()
                
                # 执行详细内容采集
                if site_rule:
                    detailed_content = crawl_detailed_content(
                        crawl_result.original_url,
                        title_xpath=site_rule.title_xpath,
                        content_xpath=site_rule.content_xpath,
                        headers=site_rule.get_request_headers()
                    )
                else:
                    detailed_content = crawl_detailed_content(crawl_result.original_url)
                
                # 检查是否需要更新规则
                if site_rule and (not detailed_content.get('title') or not detailed_content.get('content')):
                    updated = update_crawl_rules(
                        crawl_result.original_url,
                        site_rule,
                        crawl_result.title
                    )
                    if updated:
                        # 使用更新后的规则重新采集
                        detailed_content = crawl_detailed_content(
                            crawl_result.original_url,
                            title_xpath=site_rule.title_xpath,
                            content_xpath=site_rule.content_xpath,
                            headers=site_rule.get_request_headers()
                        )
                
                # 保存详细采集结果
                depth_result = DepthCrawlResult.query.filter_by(crawl_result_id=data_id).first()
                if depth_result:
                    # 更新已有结果
                    depth_result.content = detailed_content.get('content', '')
                    depth_result.set_images(detailed_content.get('images', []))
                    depth_result.set_videos(detailed_content.get('videos', []))
                    depth_result.set_links(detailed_content.get('links', []))
                    depth_result.set_meta_data(detailed_content.get('meta_data', {}))
                else:
                    # 创建新结果
                    depth_result = DepthCrawlResult(
                        crawl_result_id=data_id,
                        content=detailed_content.get('content', ''),
                        meta_data=json.dumps(detailed_content.get('meta_data', {}), ensure_ascii=False)
                    )
                    depth_result.set_images(detailed_content.get('images', []))
                    depth_result.set_videos(detailed_content.get('videos', []))
                    depth_result.set_links(detailed_content.get('links', []))
                    db.session.add(depth_result)
                
                # 更新采集状态
                crawl_result.depth_crawled = True
                crawl_result.is_stored = True
                
                success_count += 1
                
            except Exception as e:
                current_app.logger.error(f"详细内容采集失败 ID {data_id}: {str(e)}")
                fail_count += 1
        
        # 提交所有更改
        db.session.commit()
        
        # 返回结果
        return jsonify({
            'success': True,
            'message': '批量详细内容采集完成',
            'data': {
                'total': len(data_ids),
                'success_count': success_count,
                'fail_count': fail_count
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"批量详细内容采集失败: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'批量详细内容采集失败: {str(e)}'})


@warehouse_bp.route('/api/warehouse/ai_analyze', methods=['POST'])
def ai_analyze_data():
    """
    AI分析数据（预留接口）
    参数：
        data_ids - 要分析的数据ID列表
        analyze_type - 分析类型
    返回：JSON格式的分析结果
    """
    try:
        # 获取参数
        data_ids = request.form.get('data_ids')
        analyze_type = request.form.get('analyze_type', 'general')
        
        if not data_ids:
            return jsonify({'success': False, 'message': '请选择要分析的数据'})
        
        try:
            data_ids = json.loads(data_ids)
        except json.JSONDecodeError:
            return jsonify({'success': False, 'message': '数据格式错误'})
        
        if not isinstance(data_ids, list) or len(data_ids) == 0:
            return jsonify({'success': False, 'message': '请选择要分析的数据'})
        
        # TODO: 实现AI分析逻辑
        # 此处仅返回模拟结果
        
        return jsonify({
            'success': True,
            'message': 'AI分析功能正在开发中，敬请期待！',
            'analyze_type': analyze_type,
            'data_count': len(data_ids),
            'analysis_result': {
                'sentiment': 'positive',
                'keywords': ['数据采集', '舆情分析', 'AI'],
                'summary': '这是一段AI分析的示例结果，实际功能正在开发中。',
                'topics': ['技术', '数据', '分析']
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"AI分析数据失败: {str(e)}")
        return jsonify({'success': False, 'message': f'AI分析数据失败: {str(e)}'})


# AI引擎管理接口
@warehouse_bp.route('/warehouse/ai_engines', methods=['GET'])
def ai_engines_page():
    """AI引擎管理页面"""
    return render_template('warehouse/admin/ai_engines.html')

@warehouse_bp.route('/api/warehouse/ai_engines', methods=['GET'])
def get_ai_engines():
    """
    获取AI引擎列表
    参数：
        page - 页码，默认1
        limit - 每页数量，默认10
        keyword - 搜索关键词
    返回：JSON格式的AI引擎列表
    """
    try:
        from app.models import AIEngine
        
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        keyword = request.args.get('keyword', '')
        
        # 计算偏移量
        offset = (page - 1) * limit
        
        # 构建查询
        query = AIEngine.query
        
        # 关键词搜索
        if keyword:
            query = query.filter(
                AIEngine.provider_name.like(f'%{keyword}%') | 
                AIEngine.model_name.like(f'%{keyword}%')
            )
        
        # 执行查询
        total_count = query.count()
        engines = query.order_by(AIEngine.created_at.desc()).offset(offset).limit(limit).all()
        
        # 格式化结果
        data = []
        for engine in engines:
            data.append({
                'id': engine.id,
                'provider_name': engine.provider_name,
                'api_url': engine.api_url,
                'model_name': engine.model_name,
                'description': engine.description,
                'is_active': engine.is_active,
                'created_at': engine.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': engine.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'code': 0,
            'msg': '',
            'count': total_count,
            'data': data
        })
        
    except Exception as e:
        current_app.logger.error(f"获取AI引擎列表失败: {str(e)}")
        return jsonify({'code': 1, 'msg': f'获取AI引擎列表失败: {str(e)}'})

@warehouse_bp.route('/api/warehouse/ai_engines', methods=['POST'])
def add_ai_engine():
    """
    添加AI引擎
    参数：
        provider_name - 服务商名称
        api_url - API地址
        api_key - API密钥
        model_name - 模型名称
        description - 描述
    返回：JSON格式的结果
    """
    try:
        from app.models import AIEngine
        
        # 获取表单数据
        provider_name = request.form.get('provider_name')
        api_url = request.form.get('api_url')
        api_key = request.form.get('api_key')
        model_name = request.form.get('model_name')
        description = request.form.get('description')
        
        # 验证参数
        if not all([provider_name, api_url, api_key, model_name]):
            return jsonify({'code': 1, 'msg': '请填写完整的AI引擎信息'})
        
        # 创建AI引擎
        ai_engine = AIEngine(
            provider_name=provider_name,
            api_url=api_url,
            api_key=api_key,
            model_name=model_name,
            description=description
        )
        
        db.session.add(ai_engine)
        db.session.commit()
        
        return jsonify({'code': 0, 'msg': 'AI引擎添加成功'})
        
    except Exception as e:
        current_app.logger.error(f"添加AI引擎失败: {str(e)}")
        db.session.rollback()
        return jsonify({'code': 1, 'msg': f'添加AI引擎失败: {str(e)}'})

@warehouse_bp.route('/api/warehouse/ai_engines/<int:engine_id>', methods=['PUT'])
def update_ai_engine(engine_id):
    """
    更新AI引擎
    参数：
        provider_name - 服务商名称
        api_url - API地址
        api_key - API密钥（可选）
        model_name - 模型名称
        description - 描述
        is_active - 是否激活
    返回：JSON格式的结果
    """
    try:
        from app.models import AIEngine
        
        # 获取AI引擎
        ai_engine = AIEngine.query.get(engine_id)
        if not ai_engine:
            return jsonify({'code': 1, 'msg': 'AI引擎不存在'})
        
        # 获取表单数据
        provider_name = request.form.get('provider_name')
        api_url = request.form.get('api_url')
        api_key = request.form.get('api_key')
        model_name = request.form.get('model_name')
        description = request.form.get('description')
        is_active = request.form.get('is_active')
        
        # 验证参数
        if not all([provider_name, api_url, model_name]):
            return jsonify({'code': 1, 'msg': '请填写完整的AI引擎信息'})
        
        # 更新AI引擎
        ai_engine.provider_name = provider_name
        ai_engine.api_url = api_url
        if api_key:  # 只有提供了API密钥才更新
            ai_engine.api_key = api_key
        ai_engine.model_name = model_name
        ai_engine.description = description
        if is_active is not None:
            ai_engine.is_active = is_active == '1'
        
        db.session.commit()
        
        return jsonify({'code': 0, 'msg': 'AI引擎更新成功'})
        
    except Exception as e:
        current_app.logger.error(f"更新AI引擎失败: {str(e)}")
        db.session.rollback()
        return jsonify({'code': 1, 'msg': f'更新AI引擎失败: {str(e)}'})

@warehouse_bp.route('/api/warehouse/ai_engines/<int:engine_id>', methods=['DELETE'])
def delete_ai_engine(engine_id):
    """
    删除AI引擎
    参数：
        engine_id - AI引擎ID
    返回：JSON格式的结果
    """
    try:
        from app.models import AIEngine
        
        # 获取AI引擎
        ai_engine = AIEngine.query.get(engine_id)
        if not ai_engine:
            return jsonify({'code': 1, 'msg': 'AI引擎不存在'})
        
        # 删除AI引擎
        db.session.delete(ai_engine)
        db.session.commit()
        
        return jsonify({'code': 0, 'msg': 'AI引擎删除成功'})
        
    except Exception as e:
        current_app.logger.error(f"删除AI引擎失败: {str(e)}")
        db.session.rollback()
        return jsonify({'code': 1, 'msg': f'删除AI引擎失败: {str(e)}'})

@warehouse_bp.route('/api/warehouse/ai_engines/<int:engine_id>/status', methods=['PUT'])
def toggle_ai_engine_status(engine_id):
    """
    切换AI引擎状态
    参数：
        engine_id - AI引擎ID
    返回：JSON格式的结果
    """
    try:
        from app.models import AIEngine
        
        # 获取AI引擎
        ai_engine = AIEngine.query.get(engine_id)
        if not ai_engine:
            return jsonify({'code': 1, 'msg': 'AI引擎不存在'})
        
        # 切换状态
        ai_engine.is_active = not ai_engine.is_active
        
        db.session.commit()
        
        return jsonify({'code': 0, 'msg': 'AI引擎状态更新成功'})
        
    except Exception as e:
        current_app.logger.error(f"切换AI引擎状态失败: {str(e)}")
        db.session.rollback()
        return jsonify({'code': 1, 'msg': f'切换AI引擎状态失败: {str(e)}'})

@warehouse_bp.route('/api/warehouse/ai_engines/<int:engine_id>', methods=['GET'])
def get_ai_engine_detail(engine_id):
    """
    获取AI引擎详情
    参数：
        engine_id - AI引擎ID
    返回：JSON格式的AI引擎详情
    """
    try:
        from app.models import AIEngine
        
        # 获取AI引擎
        ai_engine = AIEngine.query.get(engine_id)
        if not ai_engine:
            return jsonify({'code': 1, 'msg': 'AI引擎不存在'})
        
        # 格式化结果
        data = {
            'id': ai_engine.id,
            'provider_name': ai_engine.provider_name,
            'api_url': ai_engine.api_url,
            'model_name': ai_engine.model_name,
            'description': ai_engine.description,
            'is_active': ai_engine.is_active,
            'created_at': ai_engine.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': ai_engine.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify({'code': 0, 'msg': '', 'data': data})
        
    except Exception as e:
        current_app.logger.error(f"获取AI引擎详情失败: {str(e)}")
        return jsonify({'code': 1, 'msg': f'获取AI引擎详情失败: {str(e)}'})
