from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Find the admin user
    admin = User.query.filter_by(username='admin').first()
    
    if admin:
        # Set the new password
        admin.password_hash = generate_password_hash('admin123')
        db.session.commit()
        print(f"Password for user '{admin.username}' has been changed to 'admin123'")
    else:
        # Create admin user if it doesn't exist
        new_admin = User(
            username='admin',
            email='admin@example.com',
        )
        new_admin.password_hash = generate_password_hash('admin123')
        db.session.add(new_admin)
        db.session.commit()
        print("Admin user created with password 'admin123'") 