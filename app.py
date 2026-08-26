import os
from flask import Flask
from flask_login import LoginManager
import mongoengine as db
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import User

login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    mongo_uri = app.config.get('MONGO_URI')
    try:
        if mongo_uri:
            if mongo_uri.startswith('mongodb+srv://'):
                import certifi
                db.connect(host=mongo_uri, tlsCAFile=certifi.where())
            else:
                db.connect(host=mongo_uri)
        else:
            db.connect(db='edumanage', host='localhost', port=27017)
    except Exception as e:
        print(f"Database connection setup warning: {e}")
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

    # Register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.teacher import teacher_bp
    from routes.student import student_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)

    # Ensure upload directories exist
    try:
        os.makedirs(app.config['MATERIALS_FOLDER'], exist_ok=True)
        os.makedirs(app.config['SUBMISSIONS_FOLDER'], exist_ok=True)
    except OSError:
        # Vercel functions have a read-only filesystem (except /tmp)
        pass

    # Seed on first run
    try:
        with app.app_context():
            if not User.objects.first():
                from seed import seed_database
                seed_database()
    except Exception as e:
        print(f"Warning: Database check/seeding during startup skipped: {e}")

    # Template context processor
    @app.context_processor
    def inject_globals():
        from datetime import datetime
        return {'now': datetime.utcnow()}

    # Custom Jinja2 filters
    @app.template_filter('timeago')
    def timeago_filter(dt):
        """Convert datetime to 'X ago' format."""
        from datetime import datetime
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

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
