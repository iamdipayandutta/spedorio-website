from functools import wraps
from flask import session, redirect, url_for, request, make_response
from flask_login import current_user, login_user
from datetime import timedelta
from app import User, db

def set_secure_cookie(response, user_id):
    """Set a secure, persistent cookie for admin authentication"""
    max_age = 30 * 24 * 60 * 60  # 30 days in seconds
    response.set_cookie(
        'admin_session',
        str(user_id),
        max_age=max_age,
        httponly=True,  # Prevent JavaScript access
        secure=True,    # Only send over HTTPS
        samesite='Strict'  # Prevent CSRF
    )
    return response

def check_admin_cookie():
    """Check if admin cookie is valid and authenticate user"""
    admin_id = request.cookies.get('admin_session')
    if admin_id:
        admin = User.query.filter_by(id=admin_id, is_admin=True).first()
        if admin and not current_user.is_authenticated:
            login_user(admin, remember=True, duration=timedelta(days=30))
            return True
    return False

def admin_login_required(f):
    """Decorator to check admin authentication with persistent session support"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            # Try to authenticate using cookie
            if not check_admin_cookie():
                return redirect(url_for('admin.login'))
        elif not current_user.is_admin:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

def handle_admin_login(admin):
    """Handle admin login and set persistent session"""
    login_user(admin, remember=True, duration=timedelta(days=30))
    response = make_response(redirect(url_for('admin.dashboard')))
    return set_secure_cookie(response, admin.id)

def handle_admin_logout():
    """Handle admin logout and clear persistent session"""
    response = make_response(redirect(url_for('admin.login')))
    response.delete_cookie('admin_session')
    return response 