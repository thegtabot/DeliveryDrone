import subprocess
from flask import Flask, jsonify, Response, request
from dronekit import connect
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Connect to the Pixhawk via DroneKit
vehicle = connect('/dev/ttyAMA0', wait_ready=True, baud=57600)

# Global variable for video streaming subprocess
video_process = None

# Endpoint to get drone coordinates
@app.route('/get-drone-coordinates', methods=['GET'])
def get_drone_coordinates():
    try:
        location = vehicle.location.global_frame
        return jsonify({
            'status': 'success',
            'latitude': location.lat,
            'longitude': location.lon
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Video streaming generator for MJPEG
def generate_video_stream():
    global video_process
    cmd = ['libcamera-vid', '--inline', '--nopreview', '--width', '640', '--height', '480', '--framerate', '30', '-o', '-']
    video_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        while True:
            # Read video data from the process
            frame = video_process.stdout.read(1024 * 1024)  # Adjust chunk size if necessary
            if not frame:
                break
            # Yield frame as part of the multipart response (MJPEG)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    except Exception as e:
        if isinstance(e, BrokenPipeError):
            # Client disconnected, continue to generate frames
            print("Client disconnected. Continuing to generate frames.")
        else:
            print(f"Error occurred: {e}")
    finally:
        if video_process:
            video_process.terminate()

# Endpoint for video streaming
@app.route('/video-stream', methods=['GET'])
def video_stream():
    return Response(generate_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Endpoint to stop the video stream (optional)
@app.route('/stop-video-stream', methods=['POST'])
def stop_video_stream():
    global video_process
    if video_process:
        video_process.terminate()
        video_process = None
        return jsonify({'status': 'success', 'message': 'Video stream stopped.'})
    else:
        return jsonify({'status': 'error', 'message': 'No video stream running.'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
