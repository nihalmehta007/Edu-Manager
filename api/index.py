import os
import sys

# Ensure root directory is in sys.path so modules can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app

class VercelPathMiddleware:
    """WSGI middleware to correctly map Vercel rewritten paths back to Flask routes."""
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        matched_path = environ.get('HTTP_X_MATCHED_PATH')
        if matched_path:
            # Vercel sends the original requested route in x-matched-path
            path = matched_path.split('?')[0]
            environ['PATH_INFO'] = path
        else:
            path_info = environ.get('PATH_INFO', '')
            if path_info.startswith('/api/index.py'):
                environ['PATH_INFO'] = path_info[len('/api/index.py'):] or '/'
            elif path_info.startswith('/api/index'):
                environ['PATH_INFO'] = path_info[len('/api/index'):] or '/'
            elif path_info.startswith('/api'):
                environ['PATH_INFO'] = path_info[len('/api'):] or '/'
                
        return self.wsgi_app(environ, start_response)

app = VercelPathMiddleware(flask_app)
