import os

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)  # .env always wins over system env vars
except ImportError:
    pass  # python-dotenv not installed; rely on system environment variables


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'edu-manage-secret-key-2024'
    # On Vercel, MONGO_URI must be provided via environment variables (Atlas)
    # Locally, default to local MongoDB
    if os.environ.get('VERCEL'):
        MONGO_URI = os.environ.get('MONGO_URI')
    else:
        MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/edumanage'

    # Session cookie — secure settings for Vercel (HTTPS), relaxed for local dev
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    if os.environ.get('VERCEL'):
        SESSION_COOKIE_SECURE = True
    else:
        SESSION_COOKIE_SECURE = False

    if os.environ.get('VERCEL'):
        UPLOAD_FOLDER = '/tmp/uploads'
    else:
        UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    MATERIALS_FOLDER = os.path.join(UPLOAD_FOLDER, 'materials')
    SUBMISSIONS_FOLDER = os.path.join(UPLOAD_FOLDER, 'submissions')
