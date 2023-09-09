from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import uuid
import redis



app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
r = redis.Redis()

sessions = {}  # This will hold our timer sessions.

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('create_session')
def handle_create_session():
    # Logic to create a session and return a session_id to the client.
    session_id = str(uuid.uuid4()) # Generate a random session ID.
    sessions[session_id] = { # Init the session data structure.
        'time_left': 1500,
        'status': 'paused',
        }
    emit('session_created', {'session_id': session_id})


@socketio.on('join_session')
def handle_join_session(session_id):
    # Logic to add the user to a session and return the current timer status.
    session_data = sessions.get(session_id, None)
    if session_data:
        emit('session_joined', session_data)
    else:
        emit('error', {'message': 'Session not found!'})


@socketio.on('timer_update')
def handle_timer_update(data):
    # Logic to update the server's timer status and broadcast to all users in the session.
    session_id = data['session_id']
    time_left = data['time_left']
    
    if session_id in sessions:
        sessions[session_id]['time_left'] = time_left
        emit('timer_updated', sessions[session_id], broadcast=True)
    else:
        emit('error', {'message': 'Session not found!'})

@socketio.on('action_update')
def handle_action_update(data):
    # Logic to handle timer actions and broadcast the changes.
    session_id = data['session_id']
    action = data['action']
    
    if session_id not in sessions:
        emit('error', {'message': 'Session not found!'})
        return

    if action == 'start':
        sessions[session_id]['status'] = 'running'
    elif action == 'pause':
        sessions[session_id]['status'] = 'paused'
    elif action == 'reset':
        sessions[session_id]['time_left'] = 1500  # Reset to 25 minutes.
        sessions[session_id]['status'] = 'paused'
    else:
        emit('error', {'message': 'Invalid action!'})
        return

    emit('action_updated', sessions[session_id], broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
