from app import app, db
from datetime import datetime
from sqlalchemy import text

def run_migrations():
    with app.app_context():
        print("Running database migrations...")
        
        # Check if columns exist
        columns = db.session.execute(text("PRAGMA table_info(user)")).fetchall()
        column_names = [col[1] for col in columns]
        
        # Add created_at column if it doesn't exist
        if 'created_at' not in column_names:
            print("Adding created_at column to User table...")
            db.session.execute(text("ALTER TABLE user ADD COLUMN created_at TIMESTAMP"))
        
        # Add last_login column if it doesn't exist
        if 'last_login' not in column_names:
            print("Adding last_login column to User table...")
            db.session.execute(text("ALTER TABLE user ADD COLUMN last_login TIMESTAMP"))
        
        # Set default values for created_at where it's NULL
        db.session.execute(text("UPDATE user SET created_at = :now WHERE created_at IS NULL"), {"now": datetime.utcnow()})
        
        db.session.commit()
        print("Migrations completed successfully!")

if __name__ == "__main__":
    run_migrations() 