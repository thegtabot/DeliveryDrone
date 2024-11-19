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
    Stream a pre-recorded test video, converting it from H264 to MP4 format.
    """
    h264_file = "/home/thegtabot/test_video.h264"  # Replace with the H264 video path
    ffmpeg_cmd = [
        'ffmpeg',
        '-i', h264_file,  # Input H264 video file
        '-c:v', 'libx264',  # Use H.264 codec
        '-f', 'mp4',  # Output format
        '-movflags', 'frag_keyframe+empty_moov',  # Web-compatible flags
        'pipe:1'  # Output to stdout
    ]

    try:
        print("Starting video streaming subprocess for MP4 conversion...")
        video_process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        while True:
            frame = video_process.stdout.read(1024 * 1024)  # Read 1 MB chunks
            if not frame:
                print("No more frames received from FFmpeg process.")
                break
            yield frame
    except GeneratorExit:
        print("Video stream closed by client.")
    except Exception as e:
        print(f"Error during video streaming: {e}")
    finally:
        if video_process:
            print("Terminating FFmpeg subprocess.")
            video_process.terminate()


@app.route('/video_stream', methods=['GET', 'POST'])
def video_stream():
    """
    Flask route for streaming video to clients.
    """
    if request.method == 'POST':
        return jsonify({"message": "This endpoint streams video; GET is recommended."}), 200
    return Response(generate_video_stream(), content_type='video/mp4')


@app.route('/start_stream', methods=['GET', 'POST'])
def start_stream():
    """
    Start streaming video to the remote server in the background.
    """
    global streaming
    if request.method == 'POST':
        return jsonify({"message": "Use GET to start the stream."}), 400

    if not streaming:
        streaming = True
        thread = threading.Thread(target=stream_video_to_server)
        thread.start()
        return jsonify({"status": "Streaming started to server"}), 200
    else:
        return jsonify({"status": "Streaming already in progress"}), 400


@app.route('/stop_stream', methods=['GET', 'POST'])
def stop_stream():
    """
    Stop video streaming.
    """
    global streaming
    if request.method == 'GET':
        return jsonify({"message": "Use POST to stop the stream."}), 400

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
