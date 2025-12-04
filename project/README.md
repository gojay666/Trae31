# 项目名称

## 项目描述
这是一个基于Flask框架的Web应用程序，包含用户认证、业务管理和系统设置等功能模块。

## 技术栈
- Python 3.x
- Flask
- SQLAlchemy
- Jinja2
- Bootstrap/LayUI

## 项目结构
```
project/
├── app/
│   ├── auth/          # 用户认证模块
│   ├── main/          # 主页面模块
│   ├── business/      # 业务管理模块
│   ├── system/        # 系统设置模块
│   └── __init__.py    # 应用初始化
├── migrations/        # 数据库迁移文件
├── tests/             # 测试文件
├── static/            # 静态资源文件
├── templates/         # HTML模板文件
├── docs/              # 项目文档
├── requirements/      # 依赖文件
├── tools/             # 工具脚本
├── .env               # 环境变量配置
└── README.md          # 项目说明
```

## 安装与运行

### 环境要求
- Python 3.7+
- pip

### 安装步骤
1. 克隆项目到本地
2. 安装依赖包
   ```bash
   pip install -r requirements.txt
   ```
3. 配置环境变量
   ```bash
   cp .env.example .env
   # 编辑.env文件，设置数据库等配置
   ```
4. 初始化数据库
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```
5. 运行项目
   ```bash
   flask run
   ```

## 功能模块

### 用户认证 (auth)
- 用户注册
- 用户登录
- 密码重置

### 主页面 (main)
- 首页展示
- 仪表盘

### 业务管理 (business)
- 业务数据管理
- 报表生成

### 系统设置 (system)
- 用户权限管理
- 系统参数配置

## 开发指南

### 代码规范
- 遵循PEP 8编码规范
- 使用Flask最佳实践

### 数据库迁移
```bash
# 创建迁移
flask db migrate -m "描述信息"
# 应用迁移
flask db upgrade
```

### 测试
```bash
pytest
```

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License