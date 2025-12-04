from flask import render_template
from flask_login import login_required, current_user
from app.main import bp


@bp.route('/')
def index():
    """首页视图"""
    return render_template('main/index.html', title='首页')


@bp.route('/dashboard')
@login_required
def dashboard():
    """舆情分析仪表盘，需要登录才能访问"""
    return render_template('main/dashboard.html', title='舆情分析')
