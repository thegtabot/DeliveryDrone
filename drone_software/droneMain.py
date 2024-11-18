from flask import Flask, jsonify, Response, request
from dronekit import connect
from flask_cors import CORS
import cv2
import threading

app = Flask(__name__)
CORS(app)

# Connect to the Pixhawk via DroneKit
vehicle = connect('/dev/ttyAMA0', wait_ready=True, baud=57600)

# Global variables for video streaming
video_stream_active = False
camera_thread = None
frame_buffer = None
lock = threading.Lock()

# Root endpoint for quick app status check
@app.route('/')
def home():
    return jsonify({'status': 'success', 'message': 'Drone app is running.'})

# Handle favicon.ico requests
@app.route('/favicon.ico')
def favicon():
    return "", 204  # No Content

# Endpoint to get drone coordinates
@app.route('/get-drone-coordinates', methods=['GET'])
def get_drone_coordinates():
    try:
        location = vehicle.location.global_frame
        print("Location: ", location.lat, location.lon)
        return jsonify({
            'status': 'success',
            'latitude': location.lat,
            'longitude': location.lon
        })
    except Exception as e:
        print("Error retrieving drone coordinates:", str(e))
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Function to capture video frames
def capture_frames():
    global frame_buffer, video_stream_active, lock
    cap = cv2.VideoCapture(0)  # Use the first connected camera (change index if needed)

    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        return

    while video_stream_active:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Encode the frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        with lock:
            frame_buffer = buffer.tobytes()

    cap.release()
    print("Camera thread stopped.")

# Video streaming generator
def generate_video_stream():
    global frame_buffer, video_stream_active, lock
    while video_stream_active:
        with lock:
            if frame_buffer:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_buffer + b'\r\n')
        # Slight delay to control frame rate
        cv2.waitKey(1)

# Endpoint for video streaming
@app.route('/video-stream', methods=['GET'])
def video_stream():
    global video_stream_active, camera_thread

    if not video_stream_active:
        video_stream_active = True
        camera_thread = threading.Thread(target=capture_frames)
        camera_thread.start()
        print("Video stream started.")

    print("Video stream endpoint accessed.")
    return Response(generate_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Endpoint to stop the video stream
@app.route('/stop-video-stream', methods=['POST'])
def stop_video_stream():
    global video_stream_active, camera_thread

    if video_stream_active:
        video_stream_active = False
        if camera_thread:
            camera_thread.join()
        print("Video stream stopped successfully.")
        return jsonify({'status': 'success', 'message': 'Video stream stopped.'})
    else:
        print("No video stream is currently running.")
        return jsonify({'status': 'error', 'message': 'No video stream running.'}), 400

if __name__ == '__main__':
    print("Starting Flask application...")
    app.run(host='0.0.0.0', port=5000)
