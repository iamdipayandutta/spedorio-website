from app import app, db, User
from flask_login import login_user, current_user
from flask import session
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

with app.app_context():
    print("=== Admin Login Verification ===")
    
    # Get admin user
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        print("ERROR: Admin user not found!")
        exit(1)
        
    print(f"Found user: {admin.username}")
    print(f"Email: {admin.email}")
    
    # Try to verify password
    PASSWORD = 'admin123'
    print(f"Testing password: {PASSWORD}")
    
    is_valid = admin.check_password(PASSWORD)
    print(f"Password valid: {is_valid}")
    
    if not is_valid:
        print("ERROR: Password verification failed!")
        exit(1)
    
    # Try to login
    login_success = login_user(admin)
    print(f"Login result: {'Success' if login_success else 'Failed'}")
    print(f"current_user.is_authenticated: {current_user.is_authenticated}")
    
    if not login_success:
        print("ERROR: Could not log in user!")
        exit(1)
    
    # Print success
    print("\n✅ Login verification successful!")
    print("You should now be able to log in with:")
    print(f"Username: {admin.username}")
    print(f"Password: {PASSWORD}")
    print("\nIf you still can't log in, check that:")
    print("1. The Flask application is properly routing to the login page")
    print("2. The CSRF token is being properly generated and submitted")
    print("3. The session settings are correct and persistent") 