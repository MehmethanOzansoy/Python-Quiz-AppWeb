import os
import sys

# Get the absolute path of the current directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Add the current directory to the Python path
sys.path.insert(0, BASE_DIR)

# Ensure instance directory exists
os.makedirs(os.path.join(BASE_DIR, 'instance'), exist_ok=True)

# Import after setting up paths
from app import app

# Print environment info for debugging
print(f"Working directory: {os.getcwd()}")
print(f"App instance path: {app.instance_path}")
print(f"Database path: {app.config['SQLALCHEMY_DATABASE_URI']}")
print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")

# Only initialize database the first time if needed
try:
    from app import db
    import sqlite3
    
    # Check if the database exists and has tables
    with sqlite3.connect('instance/quiz_app.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
    
    # If no tables, initialize the database
    if not tables:
        print("Initializing database...")
        with app.app_context():
            db.create_all()
except Exception as e:
    print(f"Warning: Could not check or initialize database: {e}")
    print("Try running 'python init_db.py' first to initialize the database")

if __name__ == "__main__":
    try:
        app.run(debug=True)
    except Exception as e:
        print(f"Error starting application: {e}")
        print("Try running 'python bootstrap.py' first to initialize the application") 