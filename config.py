import os

class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    UPLOAD_FOLDER = 'static/profile_pics'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
