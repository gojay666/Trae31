import pytest
from app import create_app, db
from app.models import User


@pytest.fixture(scope='module')
def test_client():
    """创建测试客户端"""
    # 创建测试应用
    app = create_app('testing')
    
    # 创建测试客户端
    testing_client = app.test_client()
    
    # 进入应用上下文
    with app.app_context():
        # 创建数据库表
        db.create_all()
        
        # 创建测试用户
        test_user = User(username='testuser', email='test@example.com')
        test_user.set_password('testpassword')
        db.session.add(test_user)
        db.session.commit()
        
        yield testing_client  # 测试在这里执行
        
        # 清理数据库
        db.drop_all()


@pytest.fixture(scope='module')
def logged_in_client(test_client):
    """创建已登录的测试客户端"""
    # 登录用户
    response = test_client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)
    
    yield test_client  # 返回已登录的客户端
    
    # 退出登录
    test_client.get('/auth/logout', follow_redirects=True)
