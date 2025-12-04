from flask_wtf import FlaskForm
# Flask 3.0.0将Markup移到了markupsafe模块
import markupsafe
# 为了兼容旧代码，将Markup添加到flask命名空间
import flask
flask.Markup = markupsafe.Markup
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User


class LoginForm(FlaskForm):
    """登录表单"""
    username = StringField('用户名', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('密码', validators=[DataRequired()])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')


class RegistrationForm(FlaskForm):
    """注册表单"""
    username = StringField('用户名', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    confirm_password = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('注册')
    
    def validate_username(self, username):
        """验证用户名是否已存在"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被使用，请选择其他用户名。')
    
    def validate_email(self, email):
        """验证邮箱是否已存在"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('该邮箱已被注册，请使用其他邮箱。')
