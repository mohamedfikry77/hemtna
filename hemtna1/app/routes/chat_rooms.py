from flask import Blueprint, request, jsonify
from app import db
from app.models import Room, RoomUser, User
from app.__init__ import socketio
from flask_socketio import emit, join_room, leave_room
from flask import url_for
from flask_jwt_extended import jwt_required, get_jwt_identity

chat_rooms_bp = Blueprint('chat_rooms', __name__)

# ========== HTTP Routes للجروبات ==========

@chat_rooms_bp.route('/groups', methods=['GET'])
@jwt_required()
def get_groups():
    """جلب جميع الجروبات"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user.user_type == 'doctor':
            # الدكتور يرى الجروبات التي أنشأها
            rooms = Room.query.filter_by(doctor_id=current_user_id).all()
        else:
            # ولي الأمر يرى الجروبات التي ينتمي إليها
            room_ids = [ru.room_id for ru in RoomUser.query.filter_by(user_id=current_user_id).all()]
            rooms = Room.query.filter(Room.id.in_(room_ids)).all()
        
        groups = []
        for room in rooms:
            # جلب أعضاء الغرفة
            members = []
            for ru in room.users:
                user_member = User.query.get(ru.user_id)
                if user_member:
                    members.append({
                        'id': user_member.id,
                        'name': f"{user_member.first_name} {user_member.last_name}",
                        'email': user_member.email,
                        'user_type': user_member.user_type
                    })
            
            groups.append({
                'id': room.id,
                'name': room.name or "غرفة بدون اسم",
                'image': url_for('static', filename='profile_pics/' + (room.image if room.image else 'default.png'), _external=True),
                'doctor_id': room.doctor_id,
                'members': members,
                'member_count': len(members)
            })
        
        return jsonify({'success': True, 'groups': groups})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_rooms_bp.route('/groups', methods=['POST'])
@jwt_required()
def create_group():
    """إنشاء مجموعة جديدة (للأطباء فقط)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user.user_type != 'doctor':
            return jsonify({'success': False, 'error': 'فقط الأطباء يمكنهم إنشاء جروبات'}), 403
        
        data = request.get_json()
        name = data.get('name')
        if not name:
            return jsonify({'success': False, 'error': 'اسم المجموعة مطلوب'}), 400
        
        room = Room(name=name, doctor_id=current_user_id)
        db.session.add(room)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'group': {
                'id': room.id,
                'name': room.name,
                'doctor_id': room.doctor_id,
                'image': url_for('static', filename='profile_pics/default.png', _external=True)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_rooms_bp.route('/groups/<int:group_id>', methods=['GET'])
@jwt_required()
def get_group(group_id):
    """جلب تفاصيل مجموعة معينة"""
    try:
        current_user_id = get_jwt_identity()
        room = Room.query.get(group_id)
        
        if not room:
            return jsonify({'success': False, 'error': 'المجموعة غير موجودة'}), 404
        
        # التحقق من الصلاحية
        user = User.query.get(current_user_id)
        if user.user_type != 'doctor' and not RoomUser.query.filter_by(room_id=group_id, user_id=current_user_id).first():
            return jsonify({'success': False, 'error': 'ليس لديك صلاحية للوصول لهذه المجموعة'}), 403
        
        # جلب الأعضاء
        members = []
        for ru in room.users:
            user_member = User.query.get(ru.user_id)
            if user_member:
                members.append({
                    'id': user_member.id,
                    'name': f"{user_member.first_name} {user_member.last_name}",
                    'email': user_member.email,
                    'user_type': user_member.user_type
                })
        
        # جلب معلومات الدكتور
        doctor = User.query.get(room.doctor_id)
        doctor_info = {
            'id': doctor.id,
            'name': f"{doctor.first_name} {doctor.last_name}",
            'email': doctor.email
        } if doctor else None
        
        return jsonify({
            'success': True,
            'group': {
                'id': room.id,
                'name': room.name or "غرفة بدون اسم",
                'image': url_for('static', filename='profile_pics/' + (room.image if room.image else 'default.png'), _external=True),
                'doctor': doctor_info,
                'members': members,
                'member_count': len(members)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_rooms_bp.route('/groups/<int:group_id>/members', methods=['POST'])
@jwt_required()
def add_member_to_group(group_id):
    """إضافة عضو للمجموعة (للأطباء فقط)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user.user_type != 'doctor':
            return jsonify({'success': False, 'error': 'فقط الأطباء يمكنهم إضافة أعضاء'}), 403
        
        room = Room.query.get(group_id)
        if not room or room.doctor_id != current_user_id:
            return jsonify({'success': False, 'error': 'المجموعة غير موجودة أو ليس لديك صلاحية'}), 404
        
        data = request.get_json()
        member_id = data.get('user_id')
        if not member_id:
            return jsonify({'success': False, 'error': 'معرف المستخدم مطلوب'}), 400
        
        # التحقق من وجود المستخدم
        member_user = User.query.get(member_id)
        if not member_user:
            return jsonify({'success': False, 'error': 'المستخدم غير موجود'}), 404
        
        # التحقق من عدم وجود العضو بالفعل
        if RoomUser.query.filter_by(room_id=group_id, user_id=member_id).first():
            return jsonify({'success': False, 'error': 'العضو موجود بالفعل في المجموعة'}), 400
        
        room_user = RoomUser(room_id=group_id, user_id=member_id)
        db.session.add(room_user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم إضافة العضو بنجاح',
            'member': {
                'id': member_user.id,
                'name': f"{member_user.first_name} {member_user.last_name}",
                'email': member_user.email,
                'user_type': member_user.user_type
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_rooms_bp.route('/groups/<int:group_id>/members/<int:member_id>', methods=['DELETE'])
@jwt_required()
def remove_member_from_group(group_id, member_id):
    """إزالة عضو من المجموعة (للأطباء فقط)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user.user_type != 'doctor':
            return jsonify({'success': False, 'error': 'فقط الأطباء يمكنهم إزالة أعضاء'}), 403
        
        room = Room.query.get(group_id)
        if not room or room.doctor_id != current_user_id:
            return jsonify({'success': False, 'error': 'المجموعة غير موجودة أو ليس لديك صلاحية'}), 404
        
        room_user = RoomUser.query.filter_by(room_id=group_id, user_id=member_id).first()
        if not room_user:
            return jsonify({'success': False, 'error': 'العضو غير موجود في المجموعة'}), 404
        
        db.session.delete(room_user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'تم إزالة العضو بنجاح'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_rooms_bp.route('/groups/<int:group_id>', methods=['DELETE'])
@jwt_required()
def delete_group(group_id):
    """حذف مجموعة (للدكتور الذي أنشأها فقط)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user.user_type != 'doctor':
            return jsonify({'success': False, 'error': 'فقط الأطباء يمكنهم حذف الجروبات'}), 403
        
        room = Room.query.get(group_id)
        if not room or room.doctor_id != current_user_id:
            return jsonify({'success': False, 'error': 'المجموعة غير موجودة أو ليس لديك صلاحية'}), 404
        
        # حذف جميع العلاقات مع الأعضاء أولاً
        RoomUser.query.filter_by(room_id=group_id).delete()
        
        # حذف الغرفة
        db.session.delete(room)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'تم حذف المجموعة بنجاح'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== SocketIO Events (الموجودة مسبقاً) ==========

# SocketIO event: إنشاء غرفة (للدكتور فقط)
@socketio.on('create_room')
def handle_create_room(data):
    # data: {name, doctor_id, image (اختياري)}
    name = data['name']
    doctor_id = data['doctor_id']
    image = data.get('image')
    room = Room(name=name, doctor_id=doctor_id, image=image)
    db.session.add(room)
    db.session.commit()
    emit('room_created', {
        'id': room.id,
        'name': room.name or "",
        'image': url_for('static', filename='profile_pics/' + (room.image if room.image else 'default.png'), _external=True),
        'doctor_id': room.doctor_id or 0
    }, broadcast=True)

# SocketIO event: إضافة مستخدم للغرفة
@socketio.on('add_user_to_room')
def handle_add_user_to_room(data):
    # data: {room_id, user_id}
    room_id = data['room_id']
    user_id = data['user_id']
    if not RoomUser.query.filter_by(room_id=room_id, user_id=user_id).first():
        ru = RoomUser(room_id=room_id, user_id=user_id)
        db.session.add(ru)
        db.session.commit()
    emit('user_added_to_room', {'room_id': room_id, 'user_id': user_id}, room=f'room_{room_id}')

# SocketIO event: حذف مستخدم من الغرفة
@socketio.on('remove_user_from_room')
def handle_remove_user_from_room(data):
    # data: {room_id, user_id}
    ru = RoomUser.query.filter_by(room_id=data['room_id'], user_id=data['user_id']).first()
    if ru:
        db.session.delete(ru)
        db.session.commit()
    emit('user_removed_from_room', {'room_id': data['room_id'], 'user_id': data['user_id']}, room=f'room_{data["room_id"]}')

# SocketIO event: حذف غرفة
@socketio.on('delete_room')
def handle_delete_room(data):
    # data: {room_id}
    room = Room.query.get(data['room_id'])
    if room:
        db.session.delete(room)
        db.session.commit()
    emit('room_deleted', {'room_id': data['room_id']}, broadcast=True)

# SocketIO event: تعديل اسم وصورة الغرفة
@socketio.on('edit_room')
def handle_edit_room(data):
    # data: {room_id, name (اختياري), image (اختياري)}
    room = Room.query.get(data['room_id'])
    if room:
        if 'name' in data:
            room.name = data['name']
        if 'image' in data:
            room.image = data['image']
        db.session.commit()
        emit('room_edited', {
            'room_id': room.id,
            'name': room.name or "",
            'image': url_for('static', filename='profile_pics/' + (room.image if room.image else 'default.png'), _external=True)
        }, broadcast=True)

# SocketIO event: جلب بيانات الغرف وأعضائها
@socketio.on('get_rooms')
def handle_get_rooms(data):
    # data: {doctor_id} أو {user_id}
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
            'name': room.name or "",
            'image': url_for('static', filename='profile_pics/' + (room.image if room.image else 'default.png'), _external=True),
            'doctor_id': room.doctor_id or 0,
            'users': users
        })
    emit('rooms_list', result)

# SocketIO event: انضمام لغرفة (نقل من messages.py)
@socketio.on('join_room')
def handle_join_room(data):
    join_room(f'room_{data["room_id"]}')
    emit('status', {'msg': f"User joined room {data['room_id']}"}, room=f'room_{data["room_id"]}')

# SocketIO event: مغادرة غرفة (نقل من messages.py)
@socketio.on('leave_room')
def handle_leave_room(data):
    leave_room(f'room_{data["room_id"]}')
    emit('status', {'msg': f"User left room {data['room_id']}"}, room=f'room_{data["room_id"]}') 