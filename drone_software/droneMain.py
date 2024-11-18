from flask import Flask, jsonify, Response, request
from dronekit import connect
from flask_cors import CORS
import subprocess
import threading

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

# Video streaming generator
def generate_video_stream():
    global video_process
    cmd = ['libcamera-vid', '--inline', '--nopreview', '--width', '640', '--height', '480', '--framerate', '30', '-o', '-']
    video_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    try:
        while True:
            # Check if the client disconnected
            if request.is_disconnected():
                print("Client disconnected. Closing video stream.")
                break

            # Read video data from the process
            frame = video_process.stdout.read(1024 * 1024)  # Adjust chunk size if necessary
            if not frame:
                break
            yield frame
    except GeneratorExit:
        # Log but don't print the message when the stream ends
        pass
    finally:
        if video_process:
            video_process.terminate()
            print("Video stream closed.")  # Only print this when the stream ends normally

# Endpoint for video streaming
@app.route('/video-stream', methods=['GET'])
def video_stream():
    return Response(generate_video_stream(), mimetype='video/mp4')

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
