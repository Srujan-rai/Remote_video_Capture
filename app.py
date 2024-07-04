from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)

cap = None

def initialize_camera(index):
    """Initialize camera capture."""
    global cap
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        print("Error: Could not open camera with index", index)
        return False
    return True

def release_camera():
    """Release camera capture."""
    global cap
    if cap is not None:
        cap.release()
        cap = None

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    camera_index = 0
    if not initialize_camera(camera_index):
        return "<h1>Error: Could not open camera.</h1>"
    return Response(process_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

def process_video():
    """Process video frames and stream."""
    global cap
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        ret, jpeg = cv2.imencode('.jpg', frame)
        if jpeg is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        release_camera()
