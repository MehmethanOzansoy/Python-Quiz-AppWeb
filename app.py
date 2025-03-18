from flask import Flask, render_template, redirect, url_for, request, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from config import config
import sqlite3

# Ensure instance directory exists
os.makedirs('instance', exist_ok=True)

# Create app
app = Flask(__name__)

# Set app name
app.config['APP_NAME'] = 'miraclgs'

# Configure the app
env = os.environ.get('FLASK_ENV', 'default')
app.config.from_object(config[env])

# Ensure uploads directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Create database
db = SQLAlchemy(app)

# Error handlers
@app.errorhandler(sqlite3.OperationalError)
def handle_sqlite_error(e):
    if 'no such column' in str(e):
        return render_template('error.html', 
                               title="Database Schema Error", 
                               message="The database schema is outdated. Please run 'python init_db.py' to update it."), 500
    elif 'unable to open database file' in str(e):
        return render_template('error.html', 
                               title="Database Connection Error", 
                               message="Could not connect to the database. Please check if the instance directory exists and is writable."), 500
    return render_template('error.html', 
                           title="Database Error", 
                           message=f"An unexpected database error occurred: {str(e)}"), 500

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', 
                           title="Server Error", 
                           message="An unexpected error occurred. Please try again later."), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', 
                           title="Page Not Found", 
                           message="The page you're looking for doesn't exist."), 404

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_teacher = db.Column(db.Boolean, default=False)
    quizzes = db.relationship('QuizAttempt', backref='user', lazy=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    questions = db.relationship('Question', backref='subject', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    topic = db.Column(db.String(200), nullable=True)
    image = db.Column(db.String(300), nullable=True)  # Dosya yolu için
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    subject = db.relationship('Subject', backref='attempts')

# Helper function for templates
@app.context_processor
def utility_processor():
    def get_user():
        if 'user_id' in session:
            return User.query.get(session['user_id'])
        return None
    return dict(get_user=get_user)

# Routes
@app.route('/')
def index():
    subjects = Subject.query.all()
    return render_template('index.html', subjects=subjects)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        
        user_exists = User.query.filter_by(username=username).first()
        
        if user_exists:
            flash('Username already exists')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        
        new_user = User(username=username, password=hashed_password)
        if user_type == 'admin':
            new_user.is_admin = True
        elif user_type == 'teacher':
            new_user.is_teacher = True
            
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password, password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
            
        session['user_id'] = user.id
        if user.is_admin:
            return redirect(url_for('admin_dashboard'))
        elif user.is_teacher:
            return redirect(url_for('teacher_dashboard'))
        else:
            return redirect(url_for('index'))
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('user_id'):
        return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('Unauthorized access')
        return redirect(url_for('index'))
        
    subjects = Subject.query.all()
    users = User.query.all()
    questions = Question.query.all()
    
    return render_template('admin_dashboard.html', subjects=subjects, users=users, questions=questions)

@app.route('/teacher/dashboard')
def teacher_dashboard():
    if not session.get('user_id'):
        return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    if not user.is_teacher and not user.is_admin:
        flash('Unauthorized access')
        return redirect(url_for('index'))
        
    subjects = Subject.query.all()
    user_questions = Question.query.filter_by(created_by=user.id).all()
    
    return render_template('teacher_dashboard.html', subjects=subjects, questions=user_questions)

@app.route('/subject/add', methods=['GET', 'POST'])
def add_subject():
    if not session.get('user_id'):
        return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('Unauthorized access')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Please provide a subject name')
            return redirect(url_for('add_subject'))
            
        new_subject = Subject(name=name)
        db.session.add(new_subject)
        db.session.commit()
        
        flash('Subject added successfully')
        return redirect(url_for('admin_dashboard'))
        
    return render_template('add_subject.html')

@app.route('/question/add', methods=['GET', 'POST'])
def add_question():
    if not session.get('user_id'):
        return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    if not user.is_teacher and not user.is_admin:
        flash('Unauthorized access')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        text = request.form.get('text')
        topic = request.form.get('topic')
        option_a = request.form.get('option_a')
        option_b = request.form.get('option_b')
        option_c = request.form.get('option_c')
        option_d = request.form.get('option_d')
        correct_answer = request.form.get('correct_answer')
        subject_name = request.form.get('subject_name')
        
        if not all([text, option_a, option_b, option_c, option_d, correct_answer, subject_name]):
            flash('All fields are required')
            return redirect(url_for('add_question'))
        
        # Check if subject exists, if not create it
        subject = Subject.query.filter_by(name=subject_name).first()
        if not subject:
            subject = Subject(name=subject_name)
            db.session.add(subject)
            db.session.commit()
        
        # Image processing
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Create a unique filename
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                new_filename = f"{timestamp}_{filename}"
                
                # Make sure upload folder exists
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                
                # Save the file
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                file.save(file_path)
                
                # Store the relative path for database
                image_path = new_filename
            
        new_question = Question(
            text=text,
            topic=topic,
            image=image_path,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_answer=correct_answer,
            subject_id=subject.id,
            created_by=user.id
        )
        
        db.session.add(new_question)
        db.session.commit()
        
        flash('Question added successfully')
        if user.is_admin:
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('teacher_dashboard'))
            
    return render_template('add_question.html')

@app.route('/quiz/<int:subject_id>')
def take_quiz(subject_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
        
    subject = Subject.query.get_or_404(subject_id)
    questions = Question.query.filter_by(subject_id=subject_id).all()
    
    if not questions:
        flash('No questions available for this subject')
        return redirect(url_for('index'))
        
    return render_template('quiz.html', subject=subject, questions=questions)

@app.route('/quiz/submit', methods=['POST'])
def submit_quiz():
    if not session.get('user_id'):
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    subject_id = request.form.get('subject_id')
    topic = request.form.get('topic')  # This might be None if it's a full subject quiz
    
    subject = Subject.query.get_or_404(subject_id)
    
    # Get questions based on whether this is a topic quiz or a full subject quiz
    if topic:
        questions = Question.query.filter_by(subject_id=subject_id, topic=topic).all()
    else:
        questions = Question.query.filter_by(subject_id=subject_id).all()
    
    score = 0
    for question in questions:
        user_answer = request.form.get(f'question_{question.id}')
        if user_answer and user_answer == question.correct_answer:
            score += 1
            
    quiz_attempt = QuizAttempt(
        user_id=user_id,
        subject_id=subject_id,
        score=score,
        total_questions=len(questions)
    )
    
    db.session.add(quiz_attempt)
    db.session.commit()
    
    percentage = (score / len(questions)) * 100 if questions else 0
    
    return render_template('quiz_result.html', score=score, total=len(questions), 
                          percentage=percentage, subject=subject, topic=topic)

@app.route('/question/delete/<int:question_id>', methods=['GET', 'POST'])
def delete_question(question_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    if not user.is_teacher and not user.is_admin:
        flash('Unauthorized access')
        return redirect(url_for('index'))
    
    question = Question.query.get_or_404(question_id)
    
    # Only allow question deletion by the creator or admin
    if question.created_by != user.id and not user.is_admin:
        flash('You can only delete questions you created')
        return redirect(url_for('teacher_dashboard'))
    
    # Keep track of subject_id before deleting the question
    subject_id = question.subject_id
    
    db.session.delete(question)
    db.session.commit()
    
    flash('Question deleted successfully')
    
    # Check if the subject has any remaining questions
    remaining_questions = Question.query.filter_by(subject_id=subject_id).count()
    
    # If no questions remain and the user is an admin, offer to delete the subject
    if remaining_questions == 0 and user.is_admin:
        flash('This subject has no more questions. You may want to delete it.')
    
    if user.is_admin:
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('teacher_dashboard'))

@app.route('/student/statistics')
def student_statistics():
    if not session.get('user_id'):
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    
    # Get all quiz attempts for the user
    attempts = QuizAttempt.query.filter_by(user_id=user_id).order_by(QuizAttempt.date.desc()).all()
    
    # Calculate overall statistics
    total_attempts = len(attempts)
    if total_attempts > 0:
        average_score = sum(attempt.score for attempt in attempts) / total_attempts
        average_percentage = (sum((attempt.score / attempt.total_questions) * 100 for attempt in attempts) / total_attempts) if total_attempts > 0 else 0
    else:
        average_score = 0
        average_percentage = 0
    
    # Group attempts by subject
    subject_stats = {}
    for attempt in attempts:
        subject_name = attempt.subject.name
        if subject_name not in subject_stats:
            subject_stats[subject_name] = {
                'attempts': 0,
                'total_score': 0,
                'total_questions': 0,
                'best_score': 0,
                'best_percentage': 0
            }
        
        stats = subject_stats[subject_name]
        stats['attempts'] += 1
        stats['total_score'] += attempt.score
        stats['total_questions'] += attempt.total_questions
        
        percentage = (attempt.score / attempt.total_questions) * 100
        if percentage > stats['best_percentage']:
            stats['best_score'] = attempt.score
            stats['best_percentage'] = percentage
    
    # Calculate average for each subject
    for subject, stats in subject_stats.items():
        stats['average_score'] = stats['total_score'] / stats['attempts']
        stats['average_percentage'] = (stats['average_score'] / (stats['total_questions'] / stats['attempts'])) * 100
    
    return render_template('student_statistics.html', 
                          attempts=attempts, 
                          total_attempts=total_attempts,
                          average_score=average_score,
                          average_percentage=average_percentage,
                          subject_stats=subject_stats)

@app.route('/subjects')
def view_subjects():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    subjects = Subject.query.all()
    
    # Group questions by subject to count topics
    subject_data = {}
    for subject in subjects:
        # Get all unique topics for this subject
        topics = db.session.query(Question.topic).filter(
            Question.subject_id == subject.id,
            Question.topic != None,  # Skip questions with no topic
            Question.topic != ''     # Skip questions with empty topic
        ).distinct().all()
        
        # Convert from list of tuples to list of strings
        topic_list = [t[0] for t in topics if t[0]]
        
        subject_data[subject.id] = {
            'name': subject.name,
            'question_count': len(subject.questions),
            'topic_count': len(topic_list),
            'topics': topic_list
        }
    
    return render_template('subjects.html', subjects=subjects, subject_data=subject_data)

@app.route('/subject/<int:subject_id>/topics')
def view_topics(subject_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    subject = Subject.query.get_or_404(subject_id)
    
    # Get all unique topics for this subject
    topics_query = db.session.query(Question.topic).filter(
        Question.subject_id == subject_id,
        Question.topic != None,  # Skip questions with no topic
        Question.topic != ''     # Skip questions with empty topic
    ).distinct().all()
    
    # Convert from list of tuples to list of strings
    topics = [t[0] for t in topics_query if t[0]]
    
    # For each topic, count questions
    topic_data = {}
    for topic in topics:
        question_count = Question.query.filter_by(
            subject_id=subject_id, 
            topic=topic
        ).count()
        
        topic_data[topic] = {
            'question_count': question_count
        }
    
    # Also get questions with no topic
    no_topic_count = Question.query.filter(
        Question.subject_id == subject_id,
        (Question.topic == None) | (Question.topic == '')
    ).count()
    
    return render_template(
        'topics.html', 
        subject=subject, 
        topics=topics, 
        topic_data=topic_data,
        no_topic_count=no_topic_count
    )

@app.route('/subject/<int:subject_id>/topic/<path:topic>')
def take_topic_quiz(subject_id, topic):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    subject = Subject.query.get_or_404(subject_id)
    
    # Get questions for this subject and topic
    questions = Question.query.filter_by(
        subject_id=subject_id,
        topic=topic
    ).all()
    
    if not questions:
        flash('No questions available for this topic')
        return redirect(url_for('view_topics', subject_id=subject_id))
    
    return render_template('quiz.html', subject=subject, questions=questions, topic=topic)

@app.route('/uploads/<path:filename>')
def serve_image(filename):
    try:
        # Ensure the path doesn't contain 'uploads' twice
        if filename.startswith('uploads/'):
            filename = filename.replace('uploads/', '', 1)
        
        # Check if file exists
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.isfile(file_path):
            # Return a default "image not found" image
            return send_from_directory('static/img', 'image-not-found.png')
            
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        app.logger.error(f"Error serving image {filename}: {str(e)}")
        # Return a default "image not found" image
        return send_from_directory('static/img', 'image-not-found.png')

if __name__ == '__main__':
    try:
        with app.app_context():
            db.create_all()
        app.run(debug=True)
    except Exception as e:
        print(f"Error initializing application: {e}")
        print("Try running 'python init_db.py' first to initialize the database") 