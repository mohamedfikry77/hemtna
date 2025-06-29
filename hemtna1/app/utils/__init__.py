from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from werkzeug.utils import secure_filename
from flask import current_app

db = SQLAlchemy()
jwt = JWTManager()
def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')

    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    from app.routes.auth import auth_bp
    from app.routes.posts import posts_bp
    from app.routes.messages import messages_bp
    from app.routes.users import users_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(posts_bp, url_prefix="/api/posts")
    app.register_blueprint(messages_bp, url_prefix="/api/messages")
    app.register_blueprint(users_bp, url_prefix="/api/users")

    @app.route('/')
    def index():
        return "🚀 Shaban created Hemtna API! It's running."

    with app.app_context():
        db.create_all()

    return app


def save_image(file, folder):
    """Save an uploaded image file to the given folder and return the filename."""
    filename = secure_filename(file.filename)
    upload_folder = os.path.join(current_app.root_path, f'static/{folder}')
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    return filename
