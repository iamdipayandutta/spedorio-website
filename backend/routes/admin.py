from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, logout_user, current_user
from app import db, User
from admin_auth import admin_login_required, handle_admin_login, handle_admin_logout, check_admin_cookie

admin = Blueprint('admin', __name__)

@admin.before_request
def check_admin_session():
    """Check for valid admin session before each request"""
    if not current_user.is_authenticated:
        check_admin_cookie()

@admin.route('/login', methods=['GET', 'POST'])
def login():
    # If already authenticated and is admin, redirect to dashboard
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.is_admin and user.check_password(password):
            return handle_admin_login(user)
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html')

@admin.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return handle_admin_logout()

@admin.route('/dashboard')
@admin_login_required
def dashboard():
    return render_template('admin/dashboard.html')

# Add other admin routes here, using @admin_login_required decorator 