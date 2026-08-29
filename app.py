import os
import sys
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_login import LoginManager
import mongoengine as db
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import User

login_manager = LoginManager()
csrf = CSRFProtect()

_db_connected = False
_db_error_message = None


def init_database(app):
    """Initialize MongoDB connection safely with timeouts for serverless environments."""
    global _db_connected, _db_error_message
    mongo_uri = app.config.get('MONGO_URI')

    try:
        if mongo_uri:
            connect_kwargs = {
                'host': mongo_uri,
                'serverSelectionTimeoutMS': 5000,
                'connectTimeoutMS': 5000
            }
            if 'mongodb+srv://' in mongo_uri or 'ssl=true' in mongo_uri.lower() or 'tls=true' in mongo_uri.lower():
                try:
                    import certifi
                    connect_kwargs['tlsCAFile'] = certifi.where()
                except ImportError:
                    pass
            db.connect(**connect_kwargs)
        else:
            db.connect(db='edumanage', host='localhost', port=27017, serverSelectionTimeoutMS=2000)
        _db_connected = True
        _db_error_message = None
    except Exception as e:
        _db_connected = False
        _db_error_message = str(e)
        print(f"Database connection warning: {e}")


def try_seed_database(app):
    """Seed initial data on startup if database is empty."""
    # Don't try seeding local database if running on Vercel without MONGO_URI
    if os.environ.get('VERCEL') and not app.config.get('MONGO_URI'):
        return

    try:
        with app.app_context():
            # Quick check if database is empty
            if User.objects.count() == 0:
                from seed import seed_database
                seed_database()
    except Exception as e:
        print(f"Seeding skipped or already initialized: {e}")


def create_app():
    """Application factory."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(Config)

    # Initialize extensions
    init_database(app)

    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.objects(id=user_id).first()
        except Exception:
            return None

    # Before request hook to catch unconfigured MongoDB on Vercel
    @app.before_request
    def check_vercel_db_configuration():
        if os.environ.get('VERCEL'):
            # Allow static files and health checks to bypass setup screen
            if (request.path.startswith('/static') or 
                request.path in ['/health', '/api/health', '/favicon.ico']):
                return None

            mongo_uri = app.config.get('MONGO_URI')
            if not mongo_uri:
                return render_template('setup_notice.html', db_error=None)

            # If connection failed earlier or is not active, check connectivity
            try:
                # Fast ping to ensure DB is reachable
                User.objects.limit(1).count()
            except Exception as e:
                return render_template('setup_notice.html', db_error=str(e))

    # Health check endpoints for monitoring and Vercel status
    @app.route('/health')
    @app.route('/api/health')
    def health():
        mongo_uri_set = bool(app.config.get('MONGO_URI'))
        db_status = "connected"
        db_err = None
        try:
            User.objects.limit(1).count()
        except Exception as e:
            db_status = "disconnected"
            db_err = str(e)

        status_code = 200 if (db_status == "connected" or not os.environ.get('VERCEL')) else 503
        return jsonify({
            "status": "healthy" if db_status == "connected" else "degraded",
            "database": db_status,
            "mongo_uri_configured": mongo_uri_set,
            "is_vercel": bool(os.environ.get('VERCEL')),
            "error": db_err
        }), status_code

    # Register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.teacher import teacher_bp
    from routes.student import student_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)

    # Ensure upload directories exist safely
    try:
        os.makedirs(app.config['MATERIALS_FOLDER'], exist_ok=True)
        os.makedirs(app.config['SUBMISSIONS_FOLDER'], exist_ok=True)
    except OSError:
        pass

    # Attempt initial seeding
    try_seed_database(app)

    # Template context processor
    @app.context_processor
    def inject_globals():
        return {'now': datetime.utcnow()}

    # Custom Jinja2 filters
    @app.template_filter('timeago')
    def timeago_filter(dt):
        """Convert datetime to 'X ago' format."""
        if not dt:
            return ''
        diff = datetime.utcnow() - dt
        seconds = diff.total_seconds()
        if seconds < 60:
            return 'just now'
        elif seconds < 3600:
            mins = int(seconds // 60)
            return f'{mins} min{"s" if mins != 1 else ""} ago'
        elif seconds < 86400:
            hours = int(seconds // 3600)
            return f'{hours} hour{"s" if hours != 1 else ""} ago'
        else:
            days = int(seconds // 86400)
            return f'{days} day{"s" if days != 1 else ""} ago'

    @app.template_filter('formatdate')
    def formatdate_filter(dt):
        """Format datetime."""
        if not dt:
            return 'N/A'
        return dt.strftime('%d %b, %Y')

    # Error handlers
    @app.errorhandler(500)
    def internal_error(e):
        import traceback
        traceback.print_exc()
        try:
            return render_template('errors/500.html', error=str(e)), 500
        except Exception:
            return '500 Internal Server Error', 500

    @app.errorhandler(404)
    def not_found_error(e):
        return render_template('errors/500.html', error="404 — Page Not Found"), 404

    return app


app = create_app()

# Vercel WSGI path fix — normalizes rewritten serverless path
if os.environ.get('VERCEL'):
    _original_wsgi = app.wsgi_app
    def _vercel_wsgi(environ, start_response):
        path = environ.get('PATH_INFO', '')
        if path.startswith('/api/index.py'):
            environ['PATH_INFO'] = path[13:] or '/'
        elif path.startswith('/api/index'):
            environ['PATH_INFO'] = path[10:] or '/'
        elif path.startswith('/app.py'):
            environ['PATH_INFO'] = path[7:] or '/'
        environ['SCRIPT_NAME'] = ''
        return _original_wsgi(environ, start_response)
    app.wsgi_app = _vercel_wsgi

if __name__ == '__main__':
    app.run(debug=True, port=5000)
