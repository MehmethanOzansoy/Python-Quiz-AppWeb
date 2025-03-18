import os
import sqlite3

# Ensure directories exist
os.makedirs('instance', exist_ok=True)
os.makedirs('static/uploads', exist_ok=True)

# Database path
db_path = 'instance/quiz_app.db'

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

print("Database initialized successfully at:", db_path) 