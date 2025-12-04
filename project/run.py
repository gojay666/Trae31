from app import create_app

# 创建应用实例，开启调试模式
app = create_app()
app.debug = True

if __name__ == '__main__':
    # 在本地开发环境下运行应用
    app.run(host='0.0.0.0', port=5000)
