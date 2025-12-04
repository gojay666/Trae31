def test_login_page(test_client):
    """测试登录页面是否正常加载"""
    response = test_client.get('/auth/login')
    assert response.status_code == 200
    assert b'用户登录' in response.data
    assert b'用户名' in response.data
    assert b'密码' in response.data


def test_login_success(test_client):
    """测试登录成功的情况"""
    response = test_client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'欢迎, testuser' in response.data
    assert b'退出登录' in response.data


def test_login_failure(test_client):
    """测试登录失败的情况"""
    response = test_client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'用户名或密码错误' in response.data


def test_logout(logged_in_client):
    """测试退出登录功能"""
    response = logged_in_client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'登录' in response.data
    assert b'注册' in response.data
