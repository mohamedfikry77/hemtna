from datetime import datetime
from hemtna1.app import db  # ✅ التعديل الصحيح هنا

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # admin / doctor / parent
    category = db.Column(db.String(50))
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    country_code = db.Column(db.String(10), nullable=True)
    child_birthdate = db.Column(db.Date, nullable=True)
    doctor_specialty = db.Column(db.String(100), nullable=True)
    child_education_level = db.Column(db.String(100), nullable=True)
    child_problem = db.Column(db.String(200), nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    views = db.Column(db.Integer, default=0)
    image = db.Column(db.String(255), nullable=True)
    likes = db.relationship('PostLike', back_populates='post', cascade='all, delete-orphan')
    comments = db.relationship('PostComment', back_populates='post', cascade='all, delete-orphan')

class PostLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post = db.relationship('Post', back_populates='likes')
    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', name='_post_user_uc'),)

class PostComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    post = db.relationship('Post', back_populates='comments')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Activity(db.Model):
    __tablename__ = 'activity'
    id = db.Column(db.Integer, primary_key=True)
    activity_name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(50), nullable=True)
    activity_image = db.Column(db.String(255), nullable=True)
    details = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    is_done = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer, default=0)
    child_name = db.Column(db.String(100), nullable=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    users = db.relationship('RoomUser', back_populates='room', cascade='all, delete-orphan')

class RoomUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room = db.relationship('Room', back_populates='users')
