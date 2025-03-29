from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Find admin user
    admin = User.query.filter_by(username='admin').first()
    
    if not admin:
        print("Admin user not found!")
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com'
        )
        db.session.add(admin)
        print("Created new admin user")
    else:
        print(f"Found existing admin: {admin.username}")
    
    # Set password using the User method to ensure proper hashing
    admin.set_password('admin123')
    db.session.commit()
    
    # Verify the password was set correctly
    verification = admin.check_password('admin123')
    
    print(f"Password reset successful: {verification}")
    print("You can now log in with:")
    print("Username: admin")
    print("Password: admin123") 