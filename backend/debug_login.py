from app import app, db, User
from werkzeug.security import check_password_hash, generate_password_hash

with app.app_context():
    # Find the admin user
    admin = User.query.filter_by(username='admin').first()
    
    if admin:
        print(f"Found user: '{admin.username}'")
        print(f"Email: '{admin.email}'")
        
        # Try the password
        test_password = 'admin123'
        result = check_password_hash(admin.password_hash, test_password)
        print(f"Password 'admin123' is {'correct' if result else 'incorrect'}")
        
        # Show current hash
        print(f"Current password hash: {admin.password_hash}")
        
        # Test the password verification method directly
        result2 = admin.check_password(test_password)
        print(f"admin.check_password() result: {'correct' if result2 else 'incorrect'}")
        
        # Regenerate the password for testing
        new_hash = generate_password_hash('admin123')
        print(f"Newly generated hash: {new_hash}")
        print(f"Verification of new hash: {check_password_hash(new_hash, 'admin123')}")
        
        # Update the password hash directly to ensure it works
        admin.password_hash = new_hash
        db.session.commit()
        print("Password hash updated to the new hash")
    else:
        print("Admin user not found!")
        print("Available users:")
        users = User.query.all()
        for user in users:
            print(f"- {user.username} ({user.email})") 