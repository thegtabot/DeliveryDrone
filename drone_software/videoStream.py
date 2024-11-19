from flask import Flask, Response, request, jsonify
import subprocess
import threading
import requests
import time

app = Flask(__name__)

# URL of the remote server where the video will be sent
server_url = 'http://192.168.1.104:5000/upload_video'  # Change to your server's IP and port

# Global variable to control streaming
streaming = False


def stream_video_to_server():
    """
    Capture video using libcamera-vid and send it to a remote server in chunks.
    """
    global streaming
    cmd = ['libcamera-vid', '--inline', '--nopreview', '-o', '-']
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        while streaming:
            # Read the H264 data from stdout
            h264_data = process.stdout.read(1024 * 1024)  # Read 1 MB chunks

            if not h264_data:
                print("Failed to grab frame, retrying...")
                time.sleep(0.1)  # Wait before retrying
                continue

            # Send the H264 data to the remote server
            try:
                headers = {'Content-Type': 'application/octet-stream'}
                response = requests.post(server_url, data=h264_data, headers=headers)

                if response.status_code != 204:
                    print(f"Failed to send frame: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Error sending frame: {e}")

            time.sleep(0.1)  # Optional: Add a small delay to limit the frame rate
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        process.terminate()
        print("Streaming to server terminated.")


def generate_video_stream():
    """
    Stream live video from the Raspberry Pi camera in real-time.
    """
    camera_cmd = [
        'libcamera-vid', '--inline', '--nopreview',
        '--width', '640', '--height', '480',
        '--framerate', '30', '-o', '-'
    ]
    ffmpeg_cmd = [
        'ffmpeg',
        '-i', '-',  # Input from stdin
        '-c:v', 'libx264',  # H.264 codec
        '-preset', 'ultrafast',  # Minimize latency
        '-f', 'mp4',  # MP4 format
        '-movflags', 'frag_keyframe+empty_moov',  # Web-compatible flags
        'pipe:1'  # Output to stdout
    ]

    # Start both subprocesses
    camera_process = subprocess.Popen(camera_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=camera_process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        while True:
            # Read and yield data in chunks
            frame = ffmpeg_process.stdout.read(1024 * 1024)
            if not frame:
                print("No more frames received from FFmpeg process.")
                break
            yield frame
    except GeneratorExit:
        print("Video stream closed by client.")
    except Exception as e:
        print(f"Error during video streaming: {e}")
    finally:
        camera_process.terminate()
        ffmpeg_process.terminate()
        print("Video streaming subprocesses terminated.")


@app.route('/video_stream', methods=['GET'])
def video_stream():
    """
    Flask route for real-time video streaming to clients.
    """
    print("Real-time video stream endpoint accessed.")
    return Response(generate_video_stream(), content_type='video/mp4')


@app.route('/start_stream', methods=['GET'])
def start_stream():
    """
    Start streaming video to the remote server in the background.
    """
    global streaming
    if streaming:
        return jsonify({"status": "Streaming already in progress"}), 400

    streaming = True
    thread = threading.Thread(target=stream_video_to_server, daemon=True)
    thread.start()
    print("Started streaming to server in the background.")
    return jsonify({"status": "Streaming started"}), 200


@app.route('/stop_stream', methods=['POST'])
def stop_stream():
    """
    Stop background video streaming to the remote server.
    """
    global streaming
    if not streaming:
        return jsonify({"status": "Streaming is not active"}), 400

    streaming = False
    print("Stopped streaming to server.")
    return jsonify({"status": "Streaming stopped"}), 200


@app.route('/favicon.ico')
def favicon():
    """
    Handle requests for /favicon.ico to suppress 404 errors.
    """
    return '', 204  # No Content


@app.errorhandler(405)
def method_not_allowed(e):
    """
    Handle HTTP 405 Method Not Allowed errors.
    """
    return jsonify({"error": "Method not allowed", "method": request.method, "url": request.url}), 405


if __name__ == '__main__':
    print("Starting Flask application...")
    app.run(host='0.0.0.0', port=5000, threaded=True)
