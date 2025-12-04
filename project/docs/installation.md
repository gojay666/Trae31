# 安装指南

## 环境要求

- Python 3.7+
- pip

## 安装步骤

### 1. 克隆项目到本地

```bash
git clone <项目地址>
cd project
```

### 2. 创建虚拟环境（可选但推荐）

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux/macOS
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖包

```bash
pip install -r requirements/requirements.txt

# 如果需要开发环境依赖
pip install -r requirements/requirements-dev.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑.env文件，设置数据库等配置
```

### 5. 初始化数据库

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. 运行项目

```bash
flask run
```

项目将在 http://localhost:5000 上运行。

## 常见问题

### 1. 数据库连接失败

确保.env文件中的数据库配置正确，并且数据库服务正在运行。

### 2. 端口被占用

可以使用其他端口运行项目：

```bash
flask run --port=5001
```

### 3. 依赖安装失败

尝试升级pip并重新安装：

```bash
pip install --upgrade pip
pip install -r requirements/requirements.txt
```
