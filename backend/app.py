from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import uuid
import redis



app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
r = redis.Redis()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('create_session')
def handle_create_session():
    # Logic to create a session and return a session_id to the client.
    session_id = str(uuid.uuid4()) # Generate a random session ID.
    r.hset(session_id, mapping={
    'time_left': 1500,
    'status': 'paused'
    })

    emit('session_created', {'session_id': session_id})


@socketio.on('join_session')
def handle_join_session(session_id):
    # Logic to add the user to a session and return the current timer status.
    session_data = r.hgetall(session_id)
    session_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in session_data.items()} if session_data else None

    if session_data:
        session_data['time_left'] = int(session_data['time_left'])  # Convert to integer
        emit('session_joined', session_data)
    else:
        emit('error', {'message': 'Session not found!'})


@socketio.on('timer_update')
def handle_timer_update(data):
    # Logic to update the server's timer status and broadcast to all users in the session.
    session_id = data['session_id']
    time_left = data['time_left']
    
    # Assuming time_left is sent as an integer from the frontend
    if r.exists(session_id):
        r.hset(session_id, 'time_left', time_left)
        
        updated_session_data = r.hgetall(session_id)
        updated_session_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in updated_session_data.items()}
        updated_session_data['time_left'] = int(updated_session_data['time_left'])  # Convert to integer
        
        emit('timer_updated', updated_session_data, broadcast=True)
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
    
    emit('action_updated', updated_session_data, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True)
