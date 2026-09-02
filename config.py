import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed; rely on system environment variables


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'edu-manage-secret-key-2024'
    # Default to local MongoDB when MONGO_URI is not set
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/edumanage'

    if os.environ.get('VERCEL'):
        UPLOAD_FOLDER = '/tmp/uploads'
    else:
        UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    MATERIALS_FOLDER = os.path.join(UPLOAD_FOLDER, 'materials')
    SUBMISSIONS_FOLDER = os.path.join(UPLOAD_FOLDER, 'submissions')
