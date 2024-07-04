from flask import Flask, render_template, Response
import cv2
import socket
import requests
import threading

app = Flask(__name__)


cap = None
frame = None

def initialize_camera(index):
    global cap
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        print("Error: Could not open camera with index", index)
        cap = None
        return False
    return True

def capture_frames():
    global cap, frame
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break
    cap.release()

@app.route('/')
def index():

    return render_template('index.html', local_ip=0, public_ip=0)

@app.route('/video_feed')
def video_feed():
    return Response(stream_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

def stream_video():
    global frame
    while True:
        if frame is None:
            continue
        ret, jpeg = cv2.imencode('.jpg', frame)
        if jpeg is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

if __name__ == "__main__":
    if initialize_camera(0):
        capture_thread = threading.Thread(target=capture_frames)
        capture_thread.start()
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("Error: Could not initialize camera.")
