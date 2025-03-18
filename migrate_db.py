from app import app, db
import os

with app.app_context():
    # Make sure instance directory exists
    os.makedirs('instance', exist_ok=True)
    
    print("Dropping all tables...")
    db.drop_all()
    print("Creating all tables with updated schema...")
    db.create_all()
    print("Database migration completed successfully!") 