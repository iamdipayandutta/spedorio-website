from app import app, db, User

def reset_admin_password():
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        
        if admin:
            print(f"Found admin user: {admin.username} ({admin.email})")
            new_password = "admin123"  # Simple password for testing
            admin.set_password(new_password)
            db.session.commit()
            print(f"Password reset successfully to: {new_password}")
        else:
            print("Admin user not found!")

if __name__ == "__main__":
    reset_admin_password() 