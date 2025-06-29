from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO

# إنشاء الكائنات العامة
db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*", async_mode="eventlet")

def create_app():
    app = Flask(__name__)

    # إعدادات التطبيق (تقدر تخصصها حسب بيئتك)
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # غيّرها حسب قاعدة بياناتك
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # تفعيل CORS
    CORS(app)

    # تهيئة قواعد البيانات و SocketIO
    db.init_app(app)
    socketio.init_app(app)

    # تسجيل الـ Blueprints
    from hemtna1.app.routes.auth import auth_bp
    from hemtna1.app.routes.users import users_bp
    from hemtna1.app.routes.messages import messages_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(messages_bp)

    return app


