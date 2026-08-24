import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'edu-manage-secret-key-2024'
    MONGODB_SETTINGS = {
        'db': 'edumanage',
        'host': 'localhost',
        'port': 27017
    }
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    MATERIALS_FOLDER = os.path.join(UPLOAD_FOLDER, 'materials')
    SUBMISSIONS_FOLDER = os.path.join(UPLOAD_FOLDER, 'submissions')
