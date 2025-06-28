"""
Routes for managing posts (CRUD, image upload, likes, comments, views).
"""
from flask import Blueprint, request, jsonify, url_for, current_app
from app import db
from app.models import Post, User, PostLike, PostComment
from app.utils import save_image

posts_bp = Blueprint('posts_bp', __name__, url_prefix="/api/posts")

def allowed_post_image(filename):
    """Check if the filename has an allowed image extension."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return filename and '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def safe_int(val, default=None):
    try:
        return int(val)
    except (TypeError, ValueError):
        return default

@posts_bp.route('/', methods=['GET'])
def get_posts():
    """Get all posts with doctor info, likes, comments, views, and image url."""
    posts = Post.query.all()
    result = []
    for post in posts:
        doctor = User.query.get(post.doctor_id) if post.doctor_id else None
        likes_count = PostLike.query.filter_by(post_id=post.id).count()
        comments_count = PostComment.query.filter_by(post_id=post.id).count()
        image_url = url_for('static', filename='post_images/' + post.image, _external=True) if post.image else None
        result.append({
            "id": post.id,
            "title": post.title or "",
            "content": post.content or "",
            "category": post.category or "",
            "timestamp": post.timestamp.isoformat() if post.timestamp else "",
            "doctor_id": post.doctor_id,
            "doctor_name": doctor.username if doctor else "",
            "doctor_picture": url_for('static', filename='profile_pics/' + (doctor.profile_picture if doctor and doctor.profile_picture else 'default.png'), _external=True),
            "likes": likes_count,
            "comments": comments_count,
            "views": post.views or 0,
            "image": image_url or ""
        })
    return jsonify({"success": True, "data": result})

@posts_bp.route('/', methods=['POST'])
def add_post():
    """Add a new post (with optional image upload)."""
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        data = request.form
        file = request.files.get('image')
    else:
        data = request.get_json()
        file = None
    if not all(k in data for k in ("title", "content")):
        return jsonify({"success": False, "error": "Missing title or content"}), 400
    image_filename = None
    if file and allowed_post_image(file.filename):
        image_filename = save_image(file, 'post_images')
    new_post = Post(
        title=data.get("title", ""),
        content=data.get("content", ""),
        category=data.get("category"),
        doctor_id=safe_int(data.get("doctor_id")),
        image=image_filename
    )
    db.session.add(new_post)
    db.session.commit()
    return jsonify({"success": True, "message": "Post created successfully"}), 201

@posts_bp.route('/<int:id>', methods=['PUT'])
def update_post(id):
    """Update an existing post."""
    post = Post.query.get(id)
    if not post:
        return jsonify({"success": False, "error": "Post not found"}), 404
    data = request.get_json()
    post.title = data.get("title", post.title)
    post.content = data.get("content", post.content)
    post.category = data.get("category", post.category)
    db.session.commit()
    return jsonify({"success": True, "message": "Post updated successfully"})

@posts_bp.route('/<int:id>', methods=['DELETE'])
def delete_post(id):
    """Delete a post by ID."""
    post = Post.query.get(id)
    if not post:
        return jsonify({"success": False, "error": "Post not found"}), 404
    db.session.delete(post)
    db.session.commit()
    return jsonify({"success": True, "message": "Post deleted successfully"})

@posts_bp.route('/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    """Like or unlike a post by user_id."""
    data = request.get_json()
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"success": False, "error": "Missing user_id"}), 400
    like = PostLike.query.filter_by(post_id=post_id, user_id=user_id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
        return jsonify({"success": True, "message": "Unliked"})
    else:
        new_like = PostLike(post_id=safe_int(post_id), user_id=safe_int(user_id))
        db.session.add(new_like)
        db.session.commit()
        return jsonify({"success": True, "message": "Liked"})

@posts_bp.route('/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    """Add a comment to a post."""
    data = request.get_json()
    user_id = data.get('user_id')
    comment = data.get('comment')
    if not user_id or not comment:
        return jsonify({"success": False, "error": "Missing user_id or comment"}), 400
    new_comment = PostComment(post_id=safe_int(post_id), user_id=safe_int(user_id), comment=comment or "")
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({"success": True, "message": "Comment added"})

@posts_bp.route('/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    """Get all comments for a post."""
    comments = PostComment.query.filter_by(post_id=post_id).order_by(PostComment.timestamp.asc()).all()
    result = []
    for c in comments:
        user = User.query.get(c.user_id)
        result.append({
            "id": c.id,
            "user_id": c.user_id,
            "username": user.username if user else "",
            "profile_picture": url_for('static', filename='profile_pics/' + (user.profile_picture if user and user.profile_picture else 'default.png'), _external=True),
            "comment": c.comment or "",
            "timestamp": c.timestamp.isoformat() if c.timestamp else "",
        })
    return jsonify({"success": True, "data": result})

@posts_bp.route('/<int:post_id>/view', methods=['POST'])
def increase_views(post_id):
    """Increase the view count for a post."""
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"success": False, "error": "Post not found"}), 404
    post.views += 1
    db.session.commit()
    return jsonify({"success": True, "views": post.views})
