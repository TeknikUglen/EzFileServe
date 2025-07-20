from flask import Flask, current_app
from dotenv import load_dotenv
from datetime import datetime
import os

def create_app(upload_folder_override=None):
    load_dotenv()

    project_root = os.path.dirname(os.path.dirname(__file__))

    template_folder = os.path.join(project_root, 'templates')
    static_folder = os.path.join(project_root, 'static')
    env_upload_folder = os.environ.get('UPLOAD_FOLDER', 'uploads')
    if os.path.isabs(env_upload_folder):
        upload_folder = env_upload_folder
    else:
        upload_folder = os.path.join(project_root, env_upload_folder)
    
    # Use override if provided
    if upload_folder_override:
        upload_folder = upload_folder_override

    os.makedirs(upload_folder, exist_ok=True)

    app = Flask(__name__,
        template_folder=template_folder,
        static_folder=static_folder,
        )

    app.config['UPLOAD_FOLDER'] = upload_folder
    app.secret_key = os.environ.get('SECRET_KEY', 'defaultsecret')
    app.config['UPLOAD_PASSWORD'] = os.environ.get('UPLOAD_PASSWORD', 'password')
    app.config['ADMIN_PASSWORD'] = os.environ.get('ADMIN_PASSWORD', 'password')
    app.config['UPLOAD_AUTH_REQUIRED'] = os.getenv('UPLOAD_AUTH_REQUIRED', 'true').lower() == 'true'
    app.config['ADMIN_AUTH_REQUIRED'] = os.getenv('ADMIN_AUTH_REQUIRED', 'true').lower() == 'true'
    app.config['HOSTS'] = os.getenv('HOSTS')
    app.config['ENABLE_ADMIN'] = os.getenv('ENABLE_ADMIN', 'true').lower() == 'true'

    @app.context_processor
    def inject_year():
        current_year = datetime.now().year
        start_year = int(os.environ.get('START_YEAR', 2025))
        if current_year > start_year:
            display_year = f"{start_year}-{current_year}"
        else:
            display_year = str(start_year)
        return dict(display_year=display_year)

    @app.context_processor
    def inject_config():
        return dict(config=current_app.config)


    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    from .errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    return app

