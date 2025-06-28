"""
Routes for managing users (CRUD, profile update, image upload).
"""
from flask import Blueprint, jsonify, request, current_app, url_for
from hemtna1.app.models import User
from hemtna1.app import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from hemtna1.app.utils import save_image

users_bp = Blueprint('users_bp', __name__, url_prefix="/api/users")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return filename and '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@users_bp.route('/', methods=['GET'])
def get_users():
    users = User.query.all()
    result = []
    for user in users:
        result.append({
            "id": user.id,
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
            "doctor_specialty": getattr(user, 'doctor_specialty', None),
            "profile_picture": url_for('static', filename='profile_pics/' + user.profile_picture) if user.profile_picture else None
        })
    return jsonify({"success": True, "data": result})

@users_bp.route('/', methods=['POST'])
def add_user():
    data = request.get_json()
    required_fields = ("username", "email", "password", "user_type", "category")
    if not data or not all(k in data for k in required_fields):
        return jsonify({"success": False, "error": "Missing required fields"}), 400
    new_user = User(
        username=data.get("username", ""),
        email=data.get("email", ""),
        password=data.get("password", ""),
        user_type=data.get("user_type", ""),
        category=data.get("category", "")
    )
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"success": True, "message": "User added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@users_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    identity = get_jwt_identity()
    user = User.query.get(id)
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404
    if identity['role'] != 'admin' and identity['id'] != user.id:
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    data = request.form
    file = request.files.get('profile_picture')
    user.email = data.get("email", user.email)
    user.user_type = data.get("user_type", user.user_type)
    user.category = data.get("category", user.category)
    user.first_name = data.get("first_name", getattr(user, 'first_name', ''))
    user.last_name = data.get("last_name", getattr(user, 'last_name', ''))
    user.phone = data.get("phone", getattr(user, 'phone', ''))
    user.country_code = data.get("country_code", getattr(user, 'country_code', ''))
    user.child_birthdate = data.get("child_birthdate", getattr(user, 'child_birthdate', None))
    if user.user_type == 'parent':
        user.child_education_level = data.get("child_education_level", getattr(user, 'child_education_level', ''))
        user.child_problem = data.get("child_problem", getattr(user, 'child_problem', ''))
    if user.user_type == 'doctor':
        user.doctor_specialty = data.get("doctor_specialty", getattr(user, 'doctor_specialty', ''))
    if file and allowed_file(file.filename):
        user.profile_picture = save_image(file, 'profile_pics')
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "User updated successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@users_bp.route('/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"success": True, "message": "User deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
