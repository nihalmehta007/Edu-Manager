from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from forms import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    """Redirect to appropriate dashboard or login."""
    if current_user.is_authenticated:
        return redirect(url_for(f'{current_user.role}.dashboard'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if current_user.is_authenticated:
        return redirect(url_for(f'{current_user.role}.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if user.status == 'inactive':
                flash('Your account is inactive. Please contact admin.', 'error')
                return render_template('auth/login.html', form=form)
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for(f'{user.role}.dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Student registration page."""
    if current_user.is_authenticated:
        return redirect(url_for(f'{current_user.role}.dashboard'))

    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.objects(email=form.email.data).first()
        if existing:
            flash('An account with this email already exists.', 'error')
            return render_template('auth/register.html', form=form)

        user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data or '',
            role='student',
            status='active'
        )
        user.set_password(form.password.data)
        user.save()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
