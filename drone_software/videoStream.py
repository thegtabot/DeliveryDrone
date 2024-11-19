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
    # Command to capture raw video using libcamera-vid
    cmd = ['libcamera-vid', '--inline', '--nopreview', '-o', '-']
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        while streaming:
            # Read the H264 data from stdout
            h264_data = process.stdout.read(1024 * 1024)  # Read 1 MB chunks

            if not h264_data:
                print("Failed to grab frame, retrying...")
                time.sleep(0.1)  # Wait before retrying
                continue  # Skip to the next iteration

            # Send the H264 data to the web server
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
    Generate video stream by piping the output of libcamera-vid into ffmpeg
    to convert it into a browser-compatible MP4 stream.
    """
    # Command to use ffmpeg for format conversion
    ffmpeg_cmd = [
        'ffmpeg',
        '-i', '-',  # Input from stdin
        '-c:v', 'libx264',  # Use H.264 codec
        '-f', 'mp4',  # Output format
        '-movflags', 'frag_keyframe+empty_moov',  # Web-compatible flags
        'pipe:1'  # Output to stdout
    ]

    # Start the ffmpeg process
    ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Command to capture raw video using libcamera-vid
    camera_cmd = ['libcamera-vid', '--inline', '--nopreview', '-o', '-']
    camera_process = subprocess.Popen(camera_cmd, stdout=ffmpeg_process.stdin, stderr=subprocess.PIPE)

    try:
        while True:
            # Read video data in chunks from ffmpeg
            data = ffmpeg_process.stdout.read(1024 * 1024)  # Read 1 MB chunks
            if not data:
                break
            yield data
    except GeneratorExit:
        camera_process.terminate()
        ffmpeg_process.terminate()
    finally:
        camera_process.terminate()
        ffmpeg_process.terminate()


@app.route('/video_stream', methods=['GET'])
def video_stream():
    """
    Flask route for streaming video to clients.
    """
    return Response(generate_video_stream(), content_type='video/mp4')


@app.route('/start_stream', methods=['POST'])
def start_stream():
    """
    Start streaming video to the remote server in the background.
    """
    global streaming
    if not streaming:
        streaming = True
        thread = threading.Thread(target=stream_video_to_server)
        thread.start()
        return jsonify({"status": "Streaming started to server"}), 200
    else:
        return jsonify({"status": "Streaming already in progress"}), 400


@app.route('/stop_stream', methods=['POST'])
def stop_stream():
    """
    Stop video streaming.
    """
    global streaming
    if streaming:
        streaming = False
        return jsonify({"status": "Streaming stopped"}), 200
    else:
        return jsonify({"status": "Streaming is not active"}), 400


@app.route('/favicon.ico')
def favicon():
    """
    Handle browser requests for /favicon.ico.
    """
    return '', 204  # No Content


@app.errorhandler(405)
def method_not_allowed(e):
    """
    Handle 405 Method Not Allowed errors.
    """
    return jsonify({"error": "Method not allowed", "method": request.method, "url": request.url}), 405


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
