import pytest
import json
from app import create_app, db
from app.models import User, Role, CrawlResult, DepthCrawlResult, SiteRule


@pytest.fixture
def client():
    """创建测试客户端"""
    app = create_app('testing')
    app_context = app.app_context()
    app_context.push()
    
    db.create_all()
    
    # 创建测试用户
    role = Role(name='admin', description='管理员')
    db.session.add(role)
    
    user = User(username='test_admin', email='test@example.com', password_hash='test', role=role)
    db.session.add(user)
    
    # 创建测试站点规则
    site_rule = SiteRule(
        site_name='test-site',
        site_url='http://test.example.com',
        title_xpath='//h1[@class="title"]',
        content_xpath='//div[@class="content"]',
        request_headers='{"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}',
        is_active=True
    )
    db.session.add(site_rule)
    
    # 创建测试采集结果
    crawl_result = CrawlResult(
        keyword='测试关键词',
        title='测试标题',
        summary='测试摘要',
        cover='http://test.example.com/cover.jpg',
        original_url='http://test.example.com/article/1',
        source='test-site',
        raw_data='{"test": "data"}',
        depth_crawled=False,
        is_stored=True
    )
    db.session.add(crawl_result)
    
    db.session.commit()
    
    with app.test_client() as client:
        # 登录测试用户
        client.post('/api/login', data={
            'username': 'test_admin',
            'password': 'test'
        })
        yield client
    
    db.session.remove()
    db.drop_all()
    app_context.pop()


def test_detailed_crawl_api(client, mocker):
    """测试单个详细内容采集API"""
    # 模拟crawl_detailed_content函数返回
    mock_crawl_content = mocker.patch('app.crawler.crawler.crawl_detailed_content')
    mock_crawl_content.return_value = {
        'title': '测试详细标题',
        'content': '测试详细内容...',
        'images': ['http://test.example.com/image1.jpg'],
        'videos': [],
        'links': [],
        'meta_data': {}
    }
    
    # 测试单个详细内容采集API
    response = client.post('/api/warehouse/detailed_crawl/1')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['message'] == '详细内容采集完成'
    
    # 验证详细采集结果是否保存
    depth_result = DepthCrawlResult.query.filter_by(crawl_result_id=1).first()
    assert depth_result is not None
    assert depth_result.content == '测试详细内容...'
    assert depth_result.images == '[]'
    assert depth_result.videos == '[]'
    assert depth_result.links == '[]'
    assert depth_result.meta_data == '{}'
    
    # 验证CrawlResult状态更新
    crawl_result = CrawlResult.query.get(1)
    assert crawl_result.depth_crawled is True


def test_batch_detailed_crawl_api(client, mocker):
    """测试批量详细内容采集API"""
    # 创建第二个测试采集结果
    crawl_result2 = CrawlResult(
        keyword='测试关键词2',
        title='测试标题2',
        summary='测试摘要2',
        cover='http://test.example.com/cover2.jpg',
        original_url='http://test.example.com/article/2',
        source='test-site',
        raw_data='{"test": "data2"}',
        depth_crawled=False,
        is_stored=True
    )
    db.session.add(crawl_result2)
    db.session.commit()
    
    # 模拟crawl_detailed_content函数返回
    mock_crawl_content = mocker.patch('app.crawler.crawler.crawl_detailed_content')
    mock_crawl_content.return_value = {
        'title': '测试详细标题',
        'content': '测试详细内容...',
        'images': [],
        'videos': [],
        'links': [],
        'meta_data': {}
    }
    
    # 测试批量详细内容采集API
    response = client.post('/api/warehouse/batch_detailed_crawl', data={
        'data_ids': json.dumps([1, 2])
    })
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['message'] == '批量详细内容采集完成'
    assert data['data']['total'] == 2
    assert data['data']['success_count'] == 2
    assert data['data']['fail_count'] == 0
    
    # 验证详细采集结果是否保存
    depth_result1 = DepthCrawlResult.query.filter_by(crawl_result_id=1).first()
    depth_result2 = DepthCrawlResult.query.filter_by(crawl_result_id=2).first()
    
    assert depth_result1 is not None
    assert depth_result2 is not None
    
    # 验证CrawlResult状态更新
    crawl_result1 = CrawlResult.query.get(1)
    crawl_result2 = CrawlResult.query.get(2)
    
    assert crawl_result1.depth_crawled is True
    assert crawl_result2.depth_crawled is True


def test_detailed_crawl_with_rule_update(client, mocker):
    """测试详细内容采集时的规则更新功能"""
    # 模拟crawl_detailed_content函数首次返回失败，然后成功
    def mock_crawl_side_effect(url, **kwargs):
        # 第一次调用返回空内容，触发规则更新
        if mock_crawl_side_effect.call_count == 1:
            mock_crawl_side_effect.call_count += 1
            return {
                'title': '',
                'content': '',
                'images': [],
                'videos': [],
                'links': [],
                'meta_data': {}
            }
        else:
            # 第二次调用返回成功结果
            return {
                'title': '测试详细标题',
                'content': '测试详细内容...',
                'images': [],
                'videos': [],
                'links': [],
                'meta_data': {}
            }
    
    mock_crawl_side_effect.call_count = 1
    
    # 模拟crawl_detailed_content函数
    mock_crawl_content = mocker.patch('app.crawler.crawler.crawl_detailed_content')
    mock_crawl_content.side_effect = mock_crawl_side_effect
    
    # 模拟update_crawl_rules函数返回成功
    mock_update_rules = mocker.patch('app.warehouse.routes.update_crawl_rules')
    mock_update_rules.return_value = True
    
    # 测试单个详细内容采集API
    response = client.post('/api/warehouse/detailed_crawl/1')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['success'] is True
    
    # 验证update_crawl_rules函数被调用
    assert mock_update_rules.called
    
    # 验证crawl_detailed_content函数被调用了两次（第一次失败，第二次成功）
    assert mock_crawl_content.call_count == 2
