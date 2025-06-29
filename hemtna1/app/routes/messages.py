from flask import Blueprint
from hemtna1.app import db, socketio
from hemtna1.app.models import Message, User
from flask_socketio import emit

messages_bp = Blueprint('messages', __name__)

@socketio.on('send_message')
def handle_send_message(data):
    msg = Message(
        message=data['message'],
        user_id=data['user_id'],
        doctor_id=data['doctor_id']
    )
    db.session.add(msg)
    db.session.commit()
    user = User.query.get(msg.user_id)
    emit('receive_message', {
        'id': msg.id,
        'message': msg.message,
        'timestamp': msg.timestamp.isoformat(),
        'user_id': msg.user_id,
        'doctor_id': msg.doctor_id,
        'username': user.username if user else "",
        'profile_picture': user.profile_picture if user and user.profile_picture else None
    }, room=data.get('room'))

@socketio.on('edit_message')
def handle_edit_message(data):
    msg = Message.query.get(data['id'])
    if msg:
        msg.message = data['new_message']
        db.session.commit()
        user = User.query.get(msg.user_id)
        emit('message_edited', {
            'id': msg.id,
            'message': msg.message,
            'username': user.username if user else "",
            'profile_picture': user.profile_picture if user and user.profile_picture else None
        }, room=data.get('room'))

@socketio.on('delete_message')
def handle_delete_message(data):
    msg = Message.query.get(data['id'])
    if msg:
        db.session.delete(msg)
        db.session.commit()
        emit('message_deleted', {'id': data['id']}, room=data.get('room'))

@socketio.on('get_messages')
def handle_get_messages(data):
    room = data.get('room')
    user_id = data.get('user_id')
    doctor_id = data.get('doctor_id')

    if room:
        messages = Message.query.all()
    elif user_id and doctor_id:
        messages = Message.query.filter_by(user_id=user_id, doctor_id=doctor_id).all()
    else:
        messages = Message.query.all()

    result = []
    for msg in messages:
        user = User.query.get(msg.user_id)
        result.append({
            'id': msg.id,
            'message': msg.message or "",
            'timestamp': msg.timestamp.isoformat() if msg.timestamp else "",
            'user_id': msg.user_id or 0,
            'doctor_id': msg.doctor_id or 0,
            'username': user.username if user else "",
            'profile_picture': user.profile_picture if user and user.profile_picture else None
        })
    emit('messages_list', result)
