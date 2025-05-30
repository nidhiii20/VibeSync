from flask import Flask, render_template, jsonify, url_for, request, redirect
from flask_socketio import SocketIO, emit
import os
import random
import subprocess
app = Flask(__name__, static_folder='static', template_folder='templates')
socketio = SocketIO(app)

# Home page
@app.route('/')
def index():
    songs = []
    song_folder  = os.path.join(app.static_folder, 'songs')
    cover_folder = os.path.join(app.static_folder, 'covers')

    for filename in os.listdir(song_folder):
        if not filename.lower().endswith('.mp3'):
            continue
        base = os.path.splitext(filename)[0]
        songs.append({
            'name':      base.replace('_', ' ').title(),
            'file_url':  f'songs/{filename}',
            'cover_url': f'covers/{base}.jpg'
        })

    return render_template('index.html', songs=songs)

# About page
@app.route('/about')
def about():
    return render_template('about.html')

# Library page
@app.route('/library')
def library():
    return render_template('library.html')

# Playlist page
def get_songs_for_mood(mood):
    music_dir = os.path.join(app.static_folder, 'music', mood)
    try:
        files = [f for f in os.listdir(music_dir) if f.lower().endswith('.mp3')]
    except FileNotFoundError:
        files = []
    songs = [
        {
            'title': os.path.splitext(fname)[0].replace('_', ' ').title(),
            'file': url_for('static', filename=f'music/{mood}/{fname}')
        }
        for fname in files
    ]
    return songs

@app.route('/playlist', methods=['GET', 'POST'])
def playlist():
    if request.method == 'POST':
        mood = request.form.get('mood')
        songs = get_songs_for_mood(mood)
        autoplay_url = random.choice(songs)['file'] if songs else None
        return render_template('playlist.html', mood=mood, songs=songs, autoplay=autoplay_url)
    return render_template('playlist.html', mood='', songs=[], autoplay=None)

@socketio.on('gesture')
def handle_gesture(data):
    print(f"Gesture received: {data['gesture']}")
    emit('gesture', data, broadcast=True)

import subprocess

gesture_process = None
gesture_running = False

@app.route("/toggle-gesture")
def toggle_gesture():
    global gesture_process, gesture_running

    if not gesture_running or gesture_process is None or gesture_process.poll() is not None:
        # Start gesture detection
        gesture_process = subprocess.Popen(["python", "NewGestures.py"])
        gesture_running = True
        return jsonify({"status": "started", "message": "Gesture detection started."})
    else:
        # Stop gesture detection
        gesture_process.terminate()
        gesture_process = None
        gesture_running = False
        return jsonify({"status": "stopped", "message": "Gesture detection stopped."})



# @app.route('/detect-emotion', methods=['POST'])
# def detect_emotion():
#     result = subprocess.run(['python', 'emotion_detector.py'], capture_output=True, text=True)
#     print("RAW OUTPUT:", result.stdout)  # <- Debug line
#     mood = result.stdout.strip().split('\n')[-1].lower()
#     songs = get_songs_for_mood(mood)
#     autoplay_url = random.choice(songs)['file'] if songs else None
#     return jsonify({'mood': mood, 'songs': songs, 'autoplay': autoplay_url})

if __name__ == '__main__':
    socketio.run(app,debug=True)
