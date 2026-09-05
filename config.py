import os

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)  # .env always wins over system env vars
except ImportError:
    pass  # python-dotenv not installed; rely on system environment variables


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'edu-manage-secret-key-2024'

    # MongoDB — always read from env var.
    # Locally: .env provides it.  On Vercel: set in dashboard.
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/edumanage')

    # Session cookie — secure on HTTPS (Vercel), relaxed locally
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = bool(os.environ.get('VERCEL'))

    # Uploads — Vercel has a read-only filesystem, use /tmp
    if os.environ.get('VERCEL'):
        UPLOAD_FOLDER = '/tmp/uploads'
    else:
        UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    MATERIALS_FOLDER = os.path.join(UPLOAD_FOLDER, 'materials')
    SUBMISSIONS_FOLDER = os.path.join(UPLOAD_FOLDER, 'submissions')
