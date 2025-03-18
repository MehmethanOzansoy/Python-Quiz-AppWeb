import sys
import os
import sqlite3
from werkzeug.security import generate_password_hash

def create_admin_user_with_app(username, password):
    """Try to create an admin user with Flask app"""
    try:
        from app import app, db, User
        
        with app.app_context():
            # Check if user already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                print(f"User '{username}' already exists!")
                return True
                
            # Create new admin user
            admin_user = User(
                username=username,
                password=generate_password_hash(password),
                is_admin=True,
                is_teacher=True
            )
            
            # Add to database
            db.session.add(admin_user)
            db.session.commit()
            
            print(f"Admin user '{username}' created successfully with app context!")
            return True
    except Exception as e:
        print(f"App context error: {e}")
        return False

def create_admin_user_direct(username, password):
    """Create admin user directly with SQLite when app context fails"""
    try:
        # Ensure instance directory exists
        os.makedirs('instance', exist_ok=True)
        
        # Connect to database
        conn = sqlite3.connect('instance/quiz_app.db')
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT * FROM user WHERE username = ?", (username,))
        if cursor.fetchone():
            print(f"User '{username}' already exists!")
            conn.close()
            return True
        
        # Create user
        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO user (username, password, is_admin, is_teacher) VALUES (?, ?, ?, ?)",
            (username, hashed_password, True, True)
        )
        
        # Commit and close
        conn.commit()
        conn.close()
        
        print(f"Admin user '{username}' created successfully with direct SQLite!")
        return True
    except Exception as e:
        print(f"Direct SQLite error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python setup_admin.py <username> <password>")
        sys.exit(1)
        
    username = sys.argv[1]
    password = sys.argv[2]
    
    # Try with app context first, fall back to direct SQLite
    if not create_admin_user_with_app(username, password):
        if not create_admin_user_direct(username, password):
            print("Failed to create admin user!")
            sys.exit(1) 