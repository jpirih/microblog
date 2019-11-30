from werkzeug.urls import url_parse

from app.auth import bp
from flask import render_template, url_for, redirect, flash, request
from flask_login import current_user, login_required, login_user, logout_user
from app.models import User
from app.auth.forms import LoginForm, ResetPasswordForm, ResetPasswordRequestForm, RegisterForm
from app.auth.email import send_password_reset_email
from app import db


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page view controller"""
    title = 'Login'
    form = LoginForm()

    # form submit
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password_hash(form.password.data):
            flash('Invalid username or password.')
            return redirect(url_for('auth.login'))
        login_user(user=user, remember=form.remember.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)

    return render_template('auth/login.html', title=title, form=form)


@bp.route('/logout')
@login_required
def logout():
    """User logout view controller"""
    logout_user()
    flash('You were successfully logged out.')
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration view controller"""
    title = 'User registration'
    form = RegisterForm()
    if form.validate_on_submit():
        User.save_user(username=form.username.data, email=form.email.data, password=form.password.data)
        flash('Congratulations you are now a registered user!')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title=title, form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """Sending request for resetting password"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    title = 'Reset Password'
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('Check your email for instructions how to reset password')
            return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', title=title, form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Form for resetting password"""
    title = 'Reset Password'
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()

    if form.validate_on_submit():
        user.set_password_hash(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password_form.html', title=title, form=form)
