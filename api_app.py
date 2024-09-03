from flask import Flask, jsonify
from models import User, Message  # Ensure these models are imported from the correct module
from models import db  # Use the shared database configuration from your main app

api_app = Flask(__name__)
api_app.config.from_object('config.Config')  # Use the same configuration as your main app
db.init_app(api_app)  # Initialize the database with this Flask app

# Ensure database tables are created before the first request
@api_app.before_request
def initialize_database():
    db.create_all()
# Add this route to api_app.py

@api_app.route('/')
def home():
    return "Welcome to the API! Available endpoints: /api/users and /api/messages", 200

# API route to get all users
@api_app.route('/api/users', methods=['GET'])
def get_users():
    try:
        users = db_session.query(User).all()
        users_data = [{"id": user.id, "username": user.username, "profile_image": user.profile_image} for user in users]
        return jsonify(users_data)
    except Exception as e:
        # Log the specific error message in the console
        print(f"Error fetching users: {e}")
        return jsonify({"error": "Failed to fetch users"}), 500


# API route to get all messages
@api_app.route('/api/messages', methods=['GET'])
def get_messages():
    try:
        messages = db_session.query(Message).all()
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


@api_app.route('/api/test_db', methods=['GET'])
def test_db():
    try:
        # Attempt a simple query to check the connection
        db_session.execute('SELECT 1')
        return jsonify({"status": "Database connection successful"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    api_app.run(port=5001)  # Run the API app on a different port to avoid conflicts

