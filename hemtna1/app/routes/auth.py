from flask import Blueprint, request, jsonify, url_for
from app import db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.auth_helpers import generate_token
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, decode_token
from datetime import timedelta, datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists"}), 400
    if User.query.filter_by(phone=data['phone']).first():
        return jsonify({"error": "Phone number already exists"}), 400

    user_type = data['user_type']
    new_user = User()
    new_user.first_name = data.get('first_name', '')
    new_user.last_name = data.get('last_name', '')
    new_user.username = f"{new_user.first_name} {new_user.last_name}".strip()
    new_user.email = data['email']
    new_user.password = generate_password_hash(data['password'])
    new_user.user_type = user_type
    new_user.category = data.get('category', '')
    new_user.phone = data['phone']
    new_user.country_code = data.get('country_code', '')
    # معالجة تاريخ الميلاد وتحويله إلى كائن تاريخ
    child_birthdate_str = data.get('child_birthdate', None)
    child_birthdate = None
    if child_birthdate_str:
        try:
            child_birthdate = datetime.strptime(child_birthdate_str, "%Y-%m-%d").date()
        except ValueError:
            child_birthdate = None
    new_user.child_birthdate = child_birthdate

    if user_type == 'parent':
        new_user.child_education_level = data.get('child_education_level', '')
        new_user.child_problem = data.get('child_problem', '')
    if user_type == 'doctor':
        new_user.doctor_specialty = data.get('doctor_specialty', '')

    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"error": "Invalid credentials"}), 401

    token = generate_token(user.id, user.user_type)
    return jsonify({"token": token, "username": user.username, "role": user.user_type})

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    identity = get_jwt_identity()
    user = User.query.get(identity['id'])
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "user_type": user.user_type,
        "category": user.category,
        "first_name": getattr(user, 'first_name', None),
        "last_name": getattr(user, 'last_name', None),
        "phone": getattr(user, 'phone', None),
        "country_code": getattr(user, 'country_code', None),
        "child_birthdate": getattr(user, 'child_birthdate', None),
        "child_education_level": getattr(user, 'child_education_level', None),
        "child_problem": getattr(user, 'child_problem', None),
        "doctor_specialty": getattr(user, 'doctor_specialty', None)
    }), 200

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "No user with this email"}), 404
    reset_token = create_access_token(identity={"id": user.id}, expires_delta=timedelta(minutes=30))
    reset_url = url_for('auth.reset_password_page', token=reset_token, _external=True)
    # في بيئة الإنتاج: أرسل الرابط بالإيميل
    # هنا: أرجع الرابط في الرد
    return jsonify({"message": "Reset link generated.", "reset_url": reset_url})

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    password = data.get('password')
    if not token or not password:
        return jsonify({"error": "Missing token or password"}), 400
    try:
        decoded = decode_token(token)
        user_id = decoded['sub']['id']
    except Exception:
        return jsonify({"error": "Invalid or expired token"}), 400
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.password = generate_password_hash(password)
    db.session.commit()
    return jsonify({"message": "Password reset successful!"})
