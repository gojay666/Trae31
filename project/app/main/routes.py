from flask import render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from app.main import bp
from app import db
from app.models import CrawlResult
import json


@bp.route('/')
def index():
    """首页视图"""
    return render_template('main/index.html', title='首页')


@bp.route('/dashboard')
@login_required
def dashboard():
    """数据采集仪表盘，需要登录才能访问"""
    return render_template('main/dashboard.html', title='数据采集')


@bp.route('/api/store_data', methods=['POST'])
@login_required
def api_store_data():
    """
    存储采集结果到数据库
    参数：
        results - 结果数据列表（JSON格式）
    返回：JSON格式的存储结果
    """
    try:
        results_json = request.form.get('results', '')
        if not results_json:
            return jsonify({'success': False, 'message': '请提供要存储的结果数据'})
        
        # 解析JSON数据
        try:
            results = json.loads(results_json)
        except json.JSONDecodeError as e:
            return jsonify({'success': False, 'message': '结果数据格式错误'})
        
        if not isinstance(results, list) or len(results) == 0:
            return jsonify({'success': False, 'message': '请提供有效的结果数据'})
        
        stored_count = 0
        
        for result in results:
            try:
                # 创建CrawlResult对象
                crawl_result = CrawlResult(
                    keyword=result.get('keyword', ''),
                    title=result.get('title', ''),
                    summary=result.get('summary', ''),
                    cover=result.get('cover', ''),
                    original_url=result.get('original_url', ''),
                    source=result.get('source', ''),
                    depth_crawled=False,
                    is_stored=True,
                    raw_data=json.dumps(result),
                    created_by=current_user.id
                )
                
                # 添加到数据库
                db.session.add(crawl_result)
                stored_count += 1
            except Exception as e:
                current_app.logger.error(f"存储单条数据失败: {str(e)}")
                continue
        
        # 提交事务
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '数据存储成功',
            'stored_count': stored_count
        })
        
    except Exception as e:
        current_app.logger.error(f"存储数据失败: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'存储数据失败: {str(e)}'})
