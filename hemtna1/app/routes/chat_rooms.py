from flask import Blueprint, request
from hemtna1.app import db, socketio
from hemtna1.app.models import Room, RoomUser, User
from flask_socketio import emit, join_room, leave_room

chat_rooms_bp = Blueprint('chat_rooms', __name__)

@socketio.on('create_room')
def handle_create_room(data):
    name = data['name']
    doctor_id = data['doctor_id']
    image = data.get('image')
    room = Room(name=name, doctor_id=doctor_id, image=image)
    db.session.add(room)
    db.session.commit()
    emit('room_created', {
        'id': room.id,
        'name': room.name,
        'image': room.image,
        'doctor_id': room.doctor_id
    }, broadcast=True)

@socketio.on('add_user_to_room')
def handle_add_user_to_room(data):
    room_id = data['room_id']
    user_id = data['user_id']
    if not RoomUser.query.filter_by(room_id=room_id, user_id=user_id).first():
        ru = RoomUser(room_id=room_id, user_id=user_id)
        db.session.add(ru)
        db.session.commit()
    emit('user_added_to_room', {'room_id': room_id, 'user_id': user_id}, room=f'room_{room_id}')

@socketio.on('remove_user_from_room')
def handle_remove_user_from_room(data):
    ru = RoomUser.query.filter_by(room_id=data['room_id'], user_id=data['user_id']).first()
    if ru:
        db.session.delete(ru)
        db.session.commit()
    emit('user_removed_from_room', {'room_id': data['room_id'], 'user_id': data['user_id']}, room=f'room_{data["room_id"]}')

@socketio.on('delete_room')
def handle_delete_room(data):
    room = Room.query.get(data['room_id'])
    if room:
        db.session.delete(room)
        db.session.commit()
    emit('room_deleted', {'room_id': data['room_id']}, broadcast=True)

@socketio.on('edit_room')
def handle_edit_room(data):
    room = Room.query.get(data['room_id'])
    if room:
        if 'name' in data:
            room.name = data['name']
        if 'image' in data:
            room.image = data['image']
        db.session.commit()
        emit('room_edited', {
            'room_id': room.id,
            'name': room.name,
            'image': room.image
        }, broadcast=True)

@socketio.on('get_rooms')
def handle_get_rooms(data):
    doctor_id = data.get('doctor_id')
    user_id = data.get('user_id')
    if doctor_id:
        rooms = Room.query.filter_by(doctor_id=doctor_id).all()
    elif user_id:
        room_ids = [ru.room_id for ru in RoomUser.query.filter_by(user_id=user_id).all()]
        rooms = Room.query.filter(Room.id.in_(room_ids)).all()
    else:
        rooms = Room.query.all()
    result = []
    for room in rooms:
        users = [ru.user_id for ru in room.users]
        result.append({
            'id': room.id,
            'name': room.name,
            'image': room.image,
            'doctor_id': room.doctor_id,
            'users': users
        })
    emit('rooms_list', result)

@socketio.on('join_room')
def handle_join_room(data):
    join_room(f'room_{data["room_id"]}')
    emit('status', {'msg': f"User joined room {data['room_id']}"}, room=f'room_{data["room_id"]}')

@socketio.on('leave_room')
def handle_leave_room(data):
    leave_room(f'room_{data["room_id"]}')
    emit('status', {'msg': f"User left room {data['room_id']}"}, room=f'room_{data["room_id"]}')
