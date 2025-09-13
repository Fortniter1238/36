from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import url_for
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

users = {}
rooms = {'main': []}

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('chat'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    if username:
        session['username'] = username
        users[username] = request.remote_addr
        return redirect(url_for('chat'))
    return redirect(url_for('index'))

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('chat.html', username=session['username'])

@socketio.on('send_message')
def handle_message(data):
    room = data.get('room', 'main')
    emit('receive_message', {'user': session['username'], 'msg': data['msg']}, room=room)

@socketio.on('join')
def on_join(data):
    room = data.get('room', 'main')
    join_room(room)
    emit('receive_message', {'user': 'System', 'msg': f"{session['username']} присоединился к чату."}, room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)