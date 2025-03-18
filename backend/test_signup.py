from app import app, db, User
from datetime import datetime

def test_user_creation():
    with app.app_context():
        # Check if DB is accessible
        try:
            users = User.query.all()
            print(f"Database connection successful. Found {len(users)} existing users.")
        except Exception as e:
            print(f"Database error: {e}")
            return
        
        # Try to create a test user
        try:
            # Check if test user already exists
            test_user = User.query.filter((User.username == 'testuser') | (User.email == 'test@example.com')).first()
            
            if test_user:
                print(f"Test user already exists with username: {test_user.username}, email: {test_user.email}")
            else:
                # Create new test user
                new_user = User(username='testuser', email='test@example.com')
                new_user.set_password('password123')
                
                db.session.add(new_user)
                db.session.commit()
                print(f"Test user created successfully with ID: {new_user.id}")
                
                # Verify the user was created
                verify_user = User.query.filter_by(username='testuser').first()
                if verify_user:
                    print("Verification successful: User exists in database")
                else:
                    print("Verification failed: User not found in database after creation")
        except Exception as e:
            print(f"Error creating test user: {e}")

if __name__ == "__main__":
    test_user_creation() 