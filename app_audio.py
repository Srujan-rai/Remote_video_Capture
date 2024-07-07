from flask import Flask, render_template, Response
import subprocess

app = Flask(__name__)

# FFmpeg command to capture video and audio
ffmpeg_command = [
    'ffmpeg',
    '-f', 'v4l2',  # Video for Linux 2 (for video capture)
    '-i', '/dev/video0',  # Default video device
    '-f', 'alsa',  # Advanced Linux Sound Architecture (for audio capture)
    '-i', 'hw:0',  # Default audio device
    '-vcodec', 'libx264',  # Video codec
    '-acodec', 'aac',  # Audio codec
    '-preset', 'veryfast',  # Encoding speed vs. compression ratio
    '-f', 'flv',  # Flash Video format (used for RTMP streams)
    'pipe:1'  # Output the stream to stdout
]

def generate():
    process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE)
    while True:
        frame = process.stdout.read(1024*64)  # Adjust buffer size as needed
        if not frame:
            break
        yield (b'--frame\r\n'
               b'Content-Type: video/x-flv\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
