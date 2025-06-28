"""
Routes for managing users (CRUD, profile update, image upload).
"""
from flask import Blueprint, jsonify, request, current_app, url_for
from app.models import User
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.utils import save_image

users_bp = Blueprint('users_bp', __name__, url_prefix="/api/users")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if the filename has an allowed image extension."""
    return filename and '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ----------- Get All Users ------------
@users_bp.route('/', methods=['GET'])
def get_users():
    """Get all users."""
    users = User.query.all()
    result = []
    for user in users:
        result.append({
            "id": user.id,
            "email": user.email or "",
            "user_type": user.user_type or "",
            "category": user.category or "",
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "phone": user.phone or "",
            "country_code": user.country_code or "",
            "child_birthdate": user.child_birthdate.isoformat() if user.child_birthdate else "",
            "child_education_level": user.child_education_level or "",
            "child_problem": user.child_problem or "",
            "doctor_specialty": user.doctor_specialty or "",
            "profile_picture": url_for('static', filename='profile_pics/' + (user.profile_picture if user.profile_picture else 'default.png'), _external=True)
        })
    return jsonify({"success": True, "data": result})

# ----------- Add New User ------------
@users_bp.route('/', methods=['POST'])
def add_user():
    """Add a new user."""
    data = request.get_json()
    required_fields = ("username", "email", "password", "user_type", "category")
    if not data or not all(k in data for k in required_fields):
        return jsonify({"success": False, "error": "Missing required fields"}), 400
    
    new_user = User()
    new_user.username = data.get("username", "")
    new_user.email = data.get("email", "")
    new_user.password = data.get("password", "")
    new_user.user_type = data.get("user_type", "")
    new_user.category = data.get("category", "")
    new_user.first_name = data.get("first_name", "")
    new_user.last_name = data.get("last_name", "")
    new_user.phone = data.get("phone", "")
    new_user.country_code = data.get("country_code", "")
    new_user.child_birthdate = data.get("child_birthdate", None)
    
    # إضافة الحقول الخاصة حسب نوع المستخدم
    if new_user.user_type == 'parent' or new_user.user_type == 'Child':
        new_user.child_education_level = data.get("child_education_level", "")
        new_user.child_problem = data.get("child_problem", "")
    if new_user.user_type == 'doctor':
        new_user.doctor_specialty = data.get("doctor_specialty", "")
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"success": True, "message": "User added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

# ----------- Edit User (Update) ------------
@users_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    """Update user profile (with optional image upload)."""
    identity = get_jwt_identity()
    # تحويل identity إلى integer إذا كان string
    user_id = int(identity) if isinstance(identity, str) else identity
    claims = get_jwt()
    user = User.query.get(id)
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404
    if claims.get('role') != 'admin' and user_id != user.id:
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    data = request.form
    file = request.files.get('profile_picture')
    # تحديث الحقول العامة
    user.email = data.get("email", user.email)
    user.user_type = data.get("user_type", user.user_type)
    user.category = data.get("category", user.category)
    user.first_name = data.get("first_name", getattr(user, 'first_name', ''))
    user.last_name = data.get("last_name", getattr(user, 'last_name', ''))
    user.phone = data.get("phone", getattr(user, 'phone', ''))
    user.country_code = data.get("country_code", getattr(user, 'country_code', ''))
    user.child_birthdate = data.get("child_birthdate", getattr(user, 'child_birthdate', None))
    # تحديث الحقول الخاصة حسب النوع
    if user.user_type == 'parent' or user.user_type == 'Child':
        user.child_education_level = data.get("child_education_level", getattr(user, 'child_education_level', ''))
        user.child_problem = data.get("child_problem", getattr(user, 'child_problem', ''))
    if user.user_type == 'doctor':
        user.doctor_specialty = data.get("doctor_specialty", getattr(user, 'doctor_specialty', ''))
    # رفع صورة شخصية إن وجدت
    if file and allowed_file(file.filename):
        user.profile_picture = save_image(file, 'profile_pics')
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "User updated successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

# ----------- Delete User ------------
@users_bp.route('/<int:id>', methods=['DELETE'])
def delete_user(id):
    """Delete a user by ID."""
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
