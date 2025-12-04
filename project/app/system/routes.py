from flask import render_template, flash, redirect, url_for, abort, jsonify, request, send_from_directory
from flask_login import login_required, current_user
from app import db
from app.system import bp
from app.models import User, Role, SystemConfig
from app.auth.forms import RegistrationForm
import os
import uuid
from werkzeug.utils import secure_filename


@bp.route('/system')
@login_required
def system_index():
    if not current_user.is_admin:
        abort(403)
    return render_template('system/index.html')

@bp.route('/system/users')
@login_required
def system_users():
    if not current_user.is_admin:
        abort(403)
    return render_template('system/users.html')

@bp.route('/system/roles')
@login_required
def system_roles():
    if not current_user.is_admin:
        abort(403)
    return render_template('system/roles.html')

@bp.route('/system/config')
@login_required
def system_config():
    if not current_user.is_admin:
        abort(403)
    # 获取系统配置
    app_config = SystemConfig.get_config()
    return render_template('system/config.html', app_config=app_config)

# 用户管理API
@bp.route('/api/users')
@login_required
def api_users():
    """获取用户列表API"""
    if not current_user.is_admin:
        return jsonify({'code': 403, 'msg': '没有权限'}), 403
    
    # 获取请求参数
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    username = request.args.get('username', '')
    email = request.args.get('email', '')
    active = request.args.get('active', '')
    is_admin = request.args.get('is_admin', '')
    
    # 构建查询
    query = User.query
    
    if username:
        query = query.filter(User.username.like(f'%{username}%'))
    if email:
        query = query.filter(User.email.like(f'%{email}%'))
    if active:
        query = query.filter(User.is_active == (active == '1'))
    if is_admin:
        query = query.filter(User.is_admin == (is_admin == '1'))
    
    # 分页查询
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    
    # 构建响应数据
    users = []
    for user in pagination.items:
        users.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'active': user.is_active,
            'is_admin': user.is_admin,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify({
        'code': 0,
        'msg': '',
        'count': pagination.total,
        'data': users
    })

@bp.route('/api/users', methods=['POST'])
@login_required
def api_add_user():
    """添加用户API"""
    if not current_user.is_admin:
        return jsonify({'code': 403, 'msg': '没有权限'}), 403
    
    # 获取表单数据
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    is_admin = request.form.get('is_admin') == '1'
    
    # 验证表单数据
    if not all([username, email, password]):
        return jsonify({'code': 400, 'msg': '请填写完整的用户信息'})
    
    # 检查用户名和邮箱是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'code': 400, 'msg': '用户名已存在'})
    
    if User.query.filter_by(email=email).first():
        return jsonify({'code': 400, 'msg': '邮箱已存在'})
    
    # 创建新用户
    user = User(username=username, email=email, is_admin=is_admin)
    user.set_password(password)
    
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({'code': 0, 'msg': '用户添加成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': f'用户添加失败: {str(e)}'})

@bp.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
def api_edit_user(user_id):
    """编辑用户API"""
    if not current_user.is_admin:
        return jsonify({'code': 403, 'msg': '没有权限'}), 403
    
    # 获取用户
    user = User.query.get_or_404(user_id)
    
    # 获取表单数据
    username = request.form.get('username')
    email = request.form.get('email')
    is_admin = request.form.get('is_admin') == '1'
    password = request.form.get('password')
    
    # 验证表单数据
    if not all([username, email]):
        return jsonify({'code': 400, 'msg': '请填写完整的用户信息'})
    
    # 检查用户名和邮箱是否已存在（排除当前用户）
    if User.query.filter_by(username=username).filter(User.id != user_id).first():
        return jsonify({'code': 400, 'msg': '用户名已存在'})
    
    if User.query.filter_by(email=email).filter(User.id != user_id).first():
        return jsonify({'code': 400, 'msg': '邮箱已存在'})
    
    # 更新用户信息
    user.username = username
    user.email = email
    user.is_admin = is_admin
    
    # 如果提供了密码，则更新密码
    if password:
        user.set_password(password)
    
    try:
        db.session.commit()
        return jsonify({'code': 0, 'msg': '用户编辑成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': f'用户编辑失败: {str(e)}'})

@bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
def api_delete_user(user_id):
    """删除用户API"""
    if not current_user.is_admin:
        return jsonify({'code': 403, 'msg': '没有权限'}), 403
    
    # 不能删除自己
    if user_id == current_user.id:
        return jsonify({'code': 400, 'msg': '不能删除自己的账户'})
    
    # 获取用户
    user = User.query.get_or_404(user_id)
    
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'code': 0, 'msg': '用户删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': f'用户删除失败: {str(e)}'})

@bp.route('/api/users/<int:user_id>/status', methods=['PUT'])
@login_required
def api_toggle_user_status(user_id):
    """切换用户状态API"""
    if not current_user.is_admin:
        return jsonify({'code': 403, 'msg': '没有权限'}), 403
    
    # 不能修改自己的状态
    if user_id == current_user.id:
        return jsonify({'code': 400, 'msg': '不能修改自己的账户状态'})
    
    # 获取用户
    user = User.query.get_or_404(user_id)
    
    # 切换状态
    user.is_active = not user.is_active
    
    try:
        db.session.commit()
        return jsonify({'code': 0, 'msg': '用户状态更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': f'用户状态更新失败: {str(e)}'})

# 角色管理API
@bp.route('/api/roles')
@login_required
def api_roles():
    """获取角色列表API"""
    if not current_user.is_admin:
        return jsonify({'code': 403, 'msg': '没有权限'}), 403
    
    # 获取请求参数
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    name = request.args.get('name', '')
    is_active = request.args.get('is_active', '')
    
    # 构建查询
    query = Role.query
    
    if name:
        query = query.filter(Role.name.like(f'%{name}%'))
    if is_active:
        query = query.filter(Role.is_active == (is_active == '1'))
    
    # 分页查询
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    
    # 构建响应数据
    roles = []
    for role in pagination.items:
        roles.append({
            'id': role.id,
            'name': role.name,
            'description': role.description,
            'permissions': role.get_permissions(),
            'is_active': role.is_active,
            'created_at': role.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify({
        'code': 0,
        'msg': '',
        'count': pagination.total,
        'data': roles
    })

@bp.route('/api/roles', methods=['POST'])
@login_required
def api_add_role():
    """添加角色API"""
    if not current_user.is_admin:
        return jsonify({'code': 403, 'msg': '没有权限'}), 403
    
    # 获取表单数据
    name = request.form.get('name')
    description = request.form.get('description')
    permissions = request.form.getlist('permissions')
    
    # 验证表单数据
    if not name:
        return jsonify({'code': 400, 'msg': '请填写角色名称'})
    
    # 检查角色名称是否已存在
    if Role.query.filter_by(name=name).first():
        return jsonify({'code': 400, 'msg': '角色名称已存在'})
    
    # 创建新角色
    role = Role(name=name, description=description)
    role.set_permissions(permissions)
    
    try:
        db.session.add(role)
        db.session.commit()
        return jsonify({'code': 0, 'msg': '角色添加成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': f'角色添加失败: {str(e)}'})

@bp.route('/api/roles/<int:role_id>', methods=['PUT'])
@login_required
def api_edit_role(role_id):
    """编辑角色API"""
    if not current_user.is_admin:
        return jsonify({'code': 403, 'msg': '没有权限'}), 403
    
    # 获取角色
    role = Role.query.get_or_404(role_id)
    
    # 获取表单数据
    name = request.form.get('name')
    description = request.form.get('description')
    permissions = request.form.getlist('permissions')
    
    # 验证表单数据
    if not name:
        return jsonify({'code': 400, 'msg': '请填写角色名称'})
    
    # 检查角色名称是否已存在（排除当前角色）
    if Role.query.filter_by(name=name).filter(Role.id != role_id).first():
        return jsonify({'code': 400, 'msg': '角色名称已存在'})
    
    # 更新角色信息
    role.name = name
    role.description = description
    role.set_permissions(permissions)
    
    try:
        db.session.commit()
        return jsonify({'code': 0, 'msg': '角色编辑成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': f'角色编辑失败: {str(e)}'})

@bp.route('/api/roles/<int:role_id>', methods=['DELETE'])
@login_required
def api_delete_role(role_id):
    """删除角色API"""
    if not current_user.is_admin:
        return jsonify({'code': 403, 'msg': '没有权限'}), 403
    
    # 不能删除管理员角色
    role = Role.query.get_or_404(role_id)
    if role.name == 'admin':
        return jsonify({'code': 400, 'msg': '不能删除管理员角色'})
    
    try:
        db.session.delete(role)
        db.session.commit()
        return jsonify({'code': 0, 'msg': '角色删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': f'角色删除失败: {str(e)}'})

@bp.route('/api/roles/<int:role_id>/users')
@login_required
def api_role_users(role_id):
    """获取角色下的用户列表API"""
    if not current_user.is_admin:
        return jsonify({'code': 403, 'msg': '没有权限'}), 403
    
    # 获取角色
    role = Role.query.get_or_404(role_id)
    
    # 获取用户列表
    users = []
    for user in role.users:
        users.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_active': user.is_active
        })
    
    return jsonify({
        'code': 0,
        'msg': '',
        'data': users
    })

# 系统配置API
@bp.route('/api/config')
@login_required
def api_get_config():
    """获取系统配置API"""
    if not current_user.is_admin:
        return jsonify({'code': 403, 'msg': '没有权限'}), 403
    
    # 获取系统配置
    config = SystemConfig.get_config()
    
    return jsonify({
        'code': 0,
        'msg': '',
        'data': config
    })

@bp.route('/api/config/basic', methods=['PUT'])
@login_required
def api_update_basic_config():
    """更新基本配置API"""
    if not current_user.is_admin:
        return jsonify({'code': 403, 'msg': '没有权限'}), 403
    
    # 获取表单数据
    data = request.get_json() or request.form.to_dict()
    
    # 更新基本配置
    for key, value in data.items():
        SystemConfig.set_by_key(key, value)
    
    return jsonify({
        'code': 0,
        'msg': '基本配置更新成功'
    })

@bp.route('/api/config/logo', methods=['PUT'])
@login_required
def api_update_logo_config():
    """更新LOGO配置API"""
    if not current_user.is_admin:
        return jsonify({'code': 403, 'msg': '没有权限'}), 403
    
    # 获取表单数据
    logo_url = request.form.get('logo_url')
    
    # 更新LOGO配置
    SystemConfig.set_by_key('logo_url', logo_url)
    
    return jsonify({
        'code': 0,
        'msg': 'LOGO配置更新成功'
    })

# 文件上传API
@bp.route('/api/upload', methods=['POST'])
@login_required
def api_upload():
    """文件上传API"""
    if not current_user.is_admin:
        return jsonify({'code': 403, 'msg': '没有权限'}), 403
    
    # 检查是否有文件上传
    if 'file' not in request.files:
        return jsonify({'code': 400, 'msg': '没有选择文件'})
    
    file = request.files['file']
    
    # 检查文件名
    if file.filename == '':
        return jsonify({'code': 400, 'msg': '没有选择文件'})
    
    # 检查文件类型
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({'code': 400, 'msg': '只允许上传图片文件(png, jpg, jpeg, gif, svg)'})
    
    # 生成唯一文件名
    filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
    
    # 确保上传目录存在
    upload_dir = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    # 保存文件
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)
    
    # 构建文件URL
    file_url = url_for('static', filename=f'uploads/{filename}', _external=True)
    
    return jsonify({
        'code': 0,
        'msg': '文件上传成功',
        'data': {
            'file_url': file_url,
            'file_path': file_path,
            'filename': filename
        }
    })

@bp.route('/api/upload/logo', methods=['POST'])
@login_required
def api_upload_logo():
    """LOGO上传API"""
    return api_upload()
