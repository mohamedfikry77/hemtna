from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_socketio import SocketIO
import os

# تهيئة الإضافات
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)

    # تحميل الإعدادات من ملف config.py في الجذر
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../config.py'))
    app.config.from_pyfile(config_path)

    # تهيئة الإضافات مع التطبيق
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    socketio.init_app(app)

    # تسجيل الـ Blueprints
    from hemtna1.app.routes.auth import auth_bp
    from hemtna1.app.routes.posts import posts_bp
    from hemtna1.app.routes.messages import messages_bp
    from hemtna1.app.routes.users import users_bp
    from hemtna1.app.routes.chat_rooms import chat_rooms_bp
    from hemtna1.app.routes.activities import activities_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(posts_bp, url_prefix="/api/posts")
    app.register_blueprint(messages_bp, url_prefix="/api/messages")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(chat_rooms_bp, url_prefix="/api/chat_rooms")
    app.register_blueprint(activities_bp, url_prefix="/api/activities")

    # إعداد صفحة البداية
    @app.route('/')
    def index():
        return "🚀 Hemtna API is Live and Running!"

    # التأكد من أن الجداول موجودة
    with app.app_context():
        db.create_all()

    return app
