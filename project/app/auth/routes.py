from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """登录视图"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('登录失败，请检查用户名和密码', 'danger')
    
    return render_template('auth/login.html', title='登录', form=form)


@bp.route('/logout')
def logout():
    """注销视图"""
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """注册视图"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功！您现在可以登录了', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='注册', form=form)
