import os
import sys
import shutil
import sqlite3
from werkzeug.security import generate_password_hash

# Current working directory
CURR_DIR = os.path.abspath(os.path.dirname(__file__))

# Ensure directories exist with proper permissions
def create_directories():
    """Create required directories"""
    print("Creating required directories...")
    
    directories = [
        os.path.join(CURR_DIR, 'instance'),
        os.path.join(CURR_DIR, 'static'),
        os.path.join(CURR_DIR, 'static/uploads'),
        os.path.join(CURR_DIR, 'static/img')
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"  Created directory: {directory}")
        else:
            print(f"  Directory already exists: {directory}")

# Create a default "image not found" image if it doesn't exist
def create_default_image():
    """Create a default image not found placeholder"""
    default_image_path = os.path.join(CURR_DIR, 'static/img/image-not-found.png')
    if not os.path.exists(default_image_path):
        print("Creating default 'image not found' placeholder...")
        
        # Simple 1x1 pixel transparent PNG
        transparent_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        
        with open(default_image_path, 'wb') as f:
            f.write(transparent_png)
        
        print(f"  Created default image: {default_image_path}")
    else:
        print(f"  Default image already exists")

# Initialize the database
def init_database():
    """Initialize the database with required tables"""
    print("Initializing database...")
    
    # Database path
    db_path = os.path.join(CURR_DIR, 'instance', 'quiz_app.db')
    
    # Connect to SQLite database (will create it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_admin BOOLEAN DEFAULT 0,
        is_teacher BOOLEAN DEFAULT 0
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subject (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS question (
        id INTEGER PRIMARY KEY,
        text TEXT NOT NULL,
        topic TEXT,
        image TEXT,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct_answer TEXT NOT NULL,
        subject_id INTEGER NOT NULL,
        created_by INTEGER NOT NULL,
        FOREIGN KEY (subject_id) REFERENCES subject (id),
        FOREIGN KEY (created_by) REFERENCES user (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quiz_attempt (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        score INTEGER NOT NULL,
        total_questions INTEGER NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES user (id),
        FOREIGN KEY (subject_id) REFERENCES subject (id)
    )
    ''')
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"  Database initialized successfully at: {db_path}")

# Create admin user
def create_admin(username, password):
    """Create an admin user in the database"""
    print(f"Creating admin user '{username}'...")
    
    # Database path
    db_path = os.path.join(CURR_DIR, 'instance', 'quiz_app.db')
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT * FROM user WHERE username = ?", (username,))
    if cursor.fetchone():
        print(f"  User '{username}' already exists")
        conn.close()
        return
    
    # Create user
    hashed_password = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO user (username, password, is_admin, is_teacher) VALUES (?, ?, ?, ?)",
        (username, hashed_password, True, True)
    )
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"  Admin user '{username}' created successfully!")

# Run all setup functions
def bootstrap_app(admin_username="admin", admin_password="admin123"):
    """Run all setup functions to bootstrap the application"""
    print("\n===== BOOTSTRAPPING MIRACLGS APPLICATION =====\n")
    
    create_directories()
    print("")
    
    create_default_image()
    print("")
    
    init_database()
    print("")
    
    create_admin(admin_username, admin_password)
    print("")
    
    print("===== BOOTSTRAP COMPLETED SUCCESSFULLY =====")
    print("\nYou can now run the application using:")
    print("  python app.py")
    print("\nLogin with:")
    print(f"  Username: {admin_username}")
    print(f"  Password: {admin_password}")

if __name__ == "__main__":
    # Get username and password from command line if provided
    admin_username = "admin"
    admin_password = "admin123"
    
    if len(sys.argv) > 1:
        admin_username = sys.argv[1]
    
    if len(sys.argv) > 2:
        admin_password = sys.argv[2]
    
    bootstrap_app(admin_username, admin_password) 