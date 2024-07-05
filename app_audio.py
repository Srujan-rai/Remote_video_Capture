from flask import Flask, render_template, Response
import cv2
import socket
import threading
import pyaudio
import wave

app = Flask(__name__)

cap = None
frame = None
audio_data = []

# Initialize the camera
def initialize_camera(index):
    global cap
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        print("Error: Could not open camera with index", index)
        cap = None
        return False
    return True

# Capture frames from the camera
def capture_frames():
    global cap, frame
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break
    cap.release()

# Record audio
def record_audio():
    global audio_data
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    while True:
        data = stream.read(CHUNK)
        audio_data.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

# Stream video
def stream_video():
    global frame
    while True:
        if frame is None:
            continue
        ret, jpeg = cv2.imencode('.jpg', frame)
        if jpeg is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

# Stream audio
@app.route('/audio_feed')
def audio_feed():
    global audio_data
    def generate():
        while True:
            if not audio_data:
                continue
            data = audio_data.pop(0)
            yield data

    return Response(generate(), mimetype="audio/x-wav")

@app.route('/')
def index():
    return render_template('index.html', local_ip=0, public_ip=0)

@app.route('/video_feed')
def video_feed():
    return Response(stream_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    if initialize_camera(0):
        capture_thread = threading.Thread(target=capture_frames)
        capture_thread.start()
        
        audio_thread = threading.Thread(target=record_audio)
        audio_thread.start()

        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("Error: Could not initialize camera.")
