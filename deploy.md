# MiraclGS - Deployment Instructions

## Prerequisites
- Python 3.12 or higher
- PostgreSQL (for production) or SQLite (for development)
- Git

## Local Deployment
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env` file
4. Initialize the database: `python init_db.py`
5. Create admin user: `python setup_admin.py admin your-secure-password`
6. Run the application: `python app.py`

## Production Deployment

### PythonAnywhere

1. Create a PythonAnywhere account (www.pythonanywhere.com)
2. Set up a new web app with manual configuration (Python 3.12)
3. Upload your project files
4. Create a virtual environment:
   ```
   mkvirtualenv --python=python3.12 miraclgs
   pip install -r requirements.txt
   ```
5. Configure environment variables:
   - Go to "Web" tab
   - Click on your web app
   - Scroll to "Environment variables"
   - Add:
     - FLASK_ENV=production
     - SECRET_KEY=your-secure-secret
     - DATABASE_URL=sqlite:///instance/quiz_app.db
     - UPLOAD_FOLDER=static/uploads

6. Set up WSGI file (`/var/www/username_pythonanywhere_com_wsgi.py`):
   ```python
   import sys
   import os

   # Add your project directory to the path
   path = '/home/yourusername/miraclgs'
   if path not in sys.path:
       sys.path.append(path)

   # Set environment variables
   os.environ['FLASK_ENV'] = 'production'
   
   # Import the app
   from wsgi import app as application
   ```

7. Initialize the database:
   ```
   cd ~/miraclgs
   python init_db.py
   python setup_admin.py admin your-secure-password
   ```

8. Restart your web app

### Heroku

1. Install Heroku CLI and log in:
   ```
   heroku login
   ```

2. Create a new Heroku app:
   ```
   heroku create miraclgs
   ```

3. Add PostgreSQL add-on:
   ```
   heroku addons:create heroku-postgresql:mini
   ```

4. Set environment variables:
   ```
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-secure-secret
   heroku config:set UPLOAD_FOLDER=static/uploads
   ```

5. Deploy the application:
   ```
   git push heroku main
   ```

6. Initialize the database:
   ```
   heroku run python init_db.py
   heroku run python setup_admin.py admin your-secure-password
   ```

7. Open the application:
   ```
   heroku open
   ```

## File Storage

For production, consider using a dedicated file storage service like AWS S3, Google Cloud Storage, or Cloudinary for storing images, as Heroku and some other platforms have an ephemeral filesystem that will lose uploaded files when the service restarts.

If using AWS S3, add the boto3 library to requirements.txt and update the application to use S3 for file storage. 