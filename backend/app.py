from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid
import redis
import os

template_dir = os.path.abspath('./templates')
static_dir = os.path.abspath('./static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
socketio = SocketIO(app, cors_allowed_origins="*")
r = redis.Redis()


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('create_room_auto')
def handle_create_session():
    # Logic to create a session and return a session_id to the client.
    session_id = str(uuid.uuid4()) # Generate a random session ID.
    r.hset(session_id, mapping={
    'time_left': 1500,
    'status': 'paused',
    'member_count': 1
    })
    r.expire(session_id, 3600)  # 1hr expiry

    join_room(session_id)
    emit('room_created_auto', {'session_id': session_id})
    r.sadd(f"members_{session_id}", request.sid)  # Add member
    # Save the mapping of request.sid to session_id in Redis immediately after creating a session.
    r.set(f"sid_{request.sid}", session_id)


@socketio.on('join_session')
def handle_join_session(session_id):
    # Check if the user is already in another session.
    prev_session_id = r.get(f"sid_{request.sid}")
    if prev_session_id:
        prev_session_id = prev_session_id.decode()
        
        # Remove the user from the previous session.
        r.srem(f"members_{prev_session_id}", request.sid)
        
        # Decrease the member_count by 1 for the previous session.
        r.hincrby(prev_session_id, 'member_count', -1)
        
        # Notify all users in the previous room about the updated member count.
        current_count = r.hget(prev_session_id, 'member_count')
        emit('update_member_count', int(current_count), room=prev_session_id)
        
        # User leaves the previous session.
        leave_room(prev_session_id)
    
    # Logic to add the user to a session and return the current timer status.
    session_data = r.hgetall(session_id)
    session_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in session_data.items()} if session_data else None

    if session_data:
        # Increase the member_count by 1.
        r.hincrby(session_id, 'member_count', 1)

        join_room(session_id)
        session_data['time_left'] = int(session_data['time_left'])  # Convert to integer
        emit('session_joined', session_data, room = session_id)

        # Notify all users in the room about the updated member count.
        current_count = int(session_data['member_count'])
        emit('update_member_count', current_count, room=session_id)
        r.sadd(f"members_{session_id}", request.sid)  # Add member

        # Save the mapping of request.sid to session_id in Redis.
        r.set(f"sid_{request.sid}", session_id)
    else:
        emit('error', {'message': 'Session not found!'})


@socketio.on('leave_session')
def handle_leave_session(session_id):
    if r.exists(session_id):
        # Decrease the member_count by 1.
        current_count = r.hincrby(session_id, 'member_count', -1)
        
        # If the user is the only member, delete all related session data from Redis.
        if current_count == 0:
            r.delete(session_id)
            r.delete(f"members_{session_id}")
        else:
            r.srem(f"members_{session_id}", request.sid)
        
        leave_room(session_id)
        
        # Notify all users in the room about the updated member count.
        emit('update_member_count', current_count, room=session_id)
        
        # Remove the mapping of request.sid to session_id from Redis.
        r.delete(f"sid_{request.sid}")
    else:
        emit('error', {'message': 'Session not found!'})



@socketio.on('disconnect')
def handle_disconnect():
    session_id = r.get(f"sid_{request.sid}")
    if session_id:
        session_id = session_id.decode()
        
        r.srem(f"members_{session_id}", request.sid)
        
        # Decrease the member_count by 1.
        current_count = r.hincrby(session_id, 'member_count', -1)
        
        # Notify all users in the room about the updated member count.
        emit('update_member_count', current_count, room=session_id)
        
        # Delete the mapping from Redis.
        r.delete(f"sid_{request.sid}")


@socketio.on('timer_update')
def handle_timer_update(data):
    # Logic to update the server's timer status and broadcast to all users in the session.
    session_id = data['session_id']
    time_left = data['time_left']
    
    # Assuming time_left is sent as an integer from the frontend
    if r.exists(session_id):
        r.hset(session_id, 'time_left', time_left)
        r.expire(session_id, 3600)  # Reset expiry while timer is running
        
        updated_session_data = r.hgetall(session_id)
        updated_session_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in updated_session_data.items()}
        updated_session_data['time_left'] = int(updated_session_data['time_left'])  # Convert to integer
        
        emit('timer_updated', updated_session_data, room = session_id)
    else:
        emit('error', {'message': 'Session not found!'})


@socketio.on('action_update')
def handle_action_update(data):
    # Logic to handle timer actions and broadcast the changes.
    session_id = data['session_id']
    action = data['action']
    
    if not r.exists(session_id):
        emit('error', {'message': 'Session not found!'})
        return

    r.expire(session_id, 3600)  # Reset expiry when actions are performed
    if action == 'start':
        r.hset(session_id, 'status', 'running')
    elif action == 'pause':
        r.hset(session_id, 'status', 'paused')
    elif action == 'reset':
        r.hset(session_id, 'time_left', 1500)
        r.hset(session_id, 'status', 'paused')
    else:
        emit('error', {'message': 'Invalid action!'})
        return

    updated_session_data = r.hgetall(session_id)
    updated_session_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in updated_session_data.items()}
    updated_session_data['time_left'] = int(updated_session_data['time_left'])  # Convert to integer
    
    emit('action_updated', updated_session_data, room = session_id)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, allow_unsafe_werkzeug=True)
