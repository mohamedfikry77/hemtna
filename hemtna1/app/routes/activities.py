"""
Routes for managing activities (CRUD, image upload, scoring, etc).
"""
from flask import Blueprint, request, jsonify, current_app, url_for
from hemtna1.app import db
from hemtna1.app.models import Activity
from hemtna1.app.utils import save_image

activities_bp = Blueprint('activities', __name__)

def allowed_activity_image(filename):
    """Check if the filename has an allowed image extension."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return filename and '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def safe_int(val, default=0):
    try:
        return int(val)
    except (TypeError, ValueError):
        return default

@activities_bp.route('/', methods=['GET'])
def get_activities():
    """Get all activities with child total score and image url."""
    activities = Activity.query.all()
    result = []
    child_scores = {}
    child_counts = {}
    for a in activities:
        child_scores.setdefault(a.child_name, 0)
        child_counts.setdefault(a.child_name, 0)
        child_scores[a.child_name] += a.score
        child_counts[a.child_name] += 1
    for a in activities:
        image_url = url_for('static', filename='activity_images/' + a.activity_image, _external=True) if a.activity_image else None
        total_score = (child_scores[a.child_name] / child_counts[a.child_name]) if child_counts[a.child_name] else 0
        result.append({
            "id": a.id,
            "activity_name": a.activity_name,
            "duration": a.duration,
            "activity_image": image_url,
            "details": a.details,
            "is_done": a.is_done,
            "score": a.score,
            "child_name": a.child_name,
            "doctor_id": a.doctor_id,
            "parent_id": a.parent_id,
            "timestamp": a.timestamp.isoformat(),
            "child_total_score": total_score
        })
    return jsonify({"success": True, "data": result})

@activities_bp.route('/', methods=['POST'])
def add_activity():
    """Add a new activity (with optional image upload)."""
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        data = request.form
        file = request.files.get('activity_image')
    else:
        data = request.get_json()
        file = None
    required = ("activity_name", "details", "child_name", "doctor_id", "parent_id")
    if not all(k in data for k in required):
        return jsonify({"success": False, "error": "Missing required fields"}), 400
    image_filename = None
    if file and allowed_activity_image(file.filename):
        image_filename = save_image(file, 'activity_images')
    activity = Activity(
        activity_name=data.get("activity_name", ""),
        duration=data.get("duration"),
        activity_image=image_filename,
        details=data.get("details", ""),
        is_done=bool(safe_int(data.get("is_done", 0))),
        score=100 if safe_int(data.get("is_done", 0)) else 0,
        child_name=data.get("child_name", ""),
        doctor_id=data.get("doctor_id"),
        parent_id=data.get("parent_id")
    )
    db.session.add(activity)
    db.session.commit()
    return jsonify({"success": True, "message": "Activity added successfully"}), 201

@activities_bp.route('/<int:id>', methods=['PUT'])
def update_activity(id):
    """Update an existing activity (with optional new image)."""
    activity = Activity.query.get(id)
    if not activity:
        return jsonify({"success": False, "error": "Activity not found"}), 404
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        data = request.form
        file = request.files.get('activity_image')
    else:
        data = request.get_json()
        file = None
    if "activity_name" in data:
        activity.activity_name = data["activity_name"]
    if "duration" in data:
        activity.duration = data["duration"]
    if "details" in data:
        activity.details = data["details"]
    if "child_name" in data:
        activity.child_name = data["child_name"]
    if "doctor_id" in data and data["doctor_id"] not in (None, ""):
        activity.doctor_id = safe_int(data["doctor_id"])
    if "parent_id" in data and data["parent_id"] not in (None, ""):
        activity.parent_id = safe_int(data["parent_id"])
    if "is_done" in data and data["is_done"] not in (None, ""):
        activity.is_done = bool(safe_int(data["is_done"]))
        activity.score = 100 if safe_int(data["is_done"]) else 0
    if file and allowed_activity_image(file.filename):
        activity.activity_image = save_image(file, 'activity_images')
    db.session.commit()
    return jsonify({"success": True, "message": "Activity updated successfully"})

@activities_bp.route('/<int:id>', methods=['DELETE'])
def delete_activity(id):
    """Delete an activity by ID."""
    activity = Activity.query.get(id)
    if not activity:
        return jsonify({"success": False, "error": "Activity not found"}), 404
    db.session.delete(activity)
    db.session.commit()
    return jsonify({"success": True, "message": "Activity deleted successfully"})
