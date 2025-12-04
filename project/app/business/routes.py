from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.business import bp
from app.models import SystemConfig


@bp.route('/')
@login_required
def index():
    """业务管理首页"""
    return render_template('business/index.html', title='业务管理')


@bp.route('/dashboard')
@login_required
def dashboard():
    """业务数据仪表盘"""
    app_config = SystemConfig.get_config()
    return render_template('business/dashboard.html', title='业务仪表盘', app_config=app_config)


@bp.route('/reports')
@login_required
def reports():
    """业务报表"""
    return render_template('business/reports.html', title='业务报表')


@bp.route('/settings')
@login_required
def settings():
    """业务设置"""
    return render_template('business/settings.html', title='业务设置')
