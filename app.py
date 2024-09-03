from flask import Flask, render_template, url_for, flash, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
import os
from models import db, User, Message

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/profile_pics'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config.from_object('config.Config')
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@app.before_request
def initialize_database():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('chat'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        if 'image' in request.files:
            image = request.files['image']
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(filepath)
                current_user.image_file = filename
                db.session.commit()
                flash('Your profile picture has been updated!', 'success')
    return render_template('profile.html', image_file=current_user.image_file)

@app.route("/chat", methods=["GET", "POST"])
@login_required
def chat():
    if request.method == "POST":
        message = request.form.get('message')
        if message:
            new_message = Message(content=message, author=current_user)
            db.session.add(new_message)
            db.session.commit()
        return redirect(url_for('chat'))

    messages = Message.query.order_by(Message.timestamp.desc()).all()
    users = User.query.all()  # Get all users to display their profile images
    return render_template('chat.html', messages=messages, users=users)

@app.route("/messages")
@login_required
def messages():
    messages = Message.query.order_by(Message.timestamp.desc()).all()
    return render_template('messages.html', messages=messages)

@app.route('/get_messages')
def get_messages():
    messages = Message.query.order_by(Message.timestamp.asc()).all()
    return render_template('messages.html', messages=messages)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# API routes
@app.route('/api/')
def home():
    return "Welcome to the API! Available endpoints: /api/users and /api/messages", 200

@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        users = db.session.query(User).all()
        users_data = [{"id": user.id, "username": user.username, "profile_image": user.image_file} for user in users]
        return jsonify(users_data)
    except Exception as e:
        print(f"Error fetching users: {e}")
        return jsonify({"error": "Failed to fetch users"}), 500

@app.route('/api/messages', methods=['GET'])
def api_get_messages():
    try:
        messages = db.session.query(Message).all()
        messages_data = [
            {
                "id": message.id,
                "content": message.content,
                "sender": message.author.username if message.author else "Unknown"
            }
            for message in messages
        ]
        return jsonify(messages_data)
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return jsonify({"error": "Failed to fetch messages"}), 500

@app.route('/api/test_db', methods=['GET'])
def test_db():
    try:
        db.session.execute('SELECT 1')
        return jsonify({"status": "Database connection successful"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
