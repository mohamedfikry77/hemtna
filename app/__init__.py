"""
Flask app factory and global extensions registration.
- Registers all blueprints (auth, posts, messages, users, main, chat_rooms)
- Initializes: DB, JWT, Migrate, SocketIO, CORS
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_socketio import SocketIO

# --- Global extensions ---
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    """
    Application factory: creates and configures the Flask app instance.
    """
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')

    # --- Initialize extensions ---
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    socketio.init_app(app)

    # --- Register blueprints (routes) ---
    from app.routes.auth import auth_bp
    from app.routes.posts import posts_bp
    from app.routes.messages import messages_bp
    from app.routes.users import users_bp
    from app.routes.chat_rooms import chat_rooms_bp
    from app.routes.activities import activities_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(posts_bp, url_prefix="/api/posts")
    app.register_blueprint(messages_bp, url_prefix="/api/messages")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(chat_rooms_bp)
    app.register_blueprint(activities_bp, url_prefix="/api/activities")

    # --- Create DB tables if not exist ---
    with app.app_context():
        db.create_all()

    return app
