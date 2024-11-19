from flask import Flask, request, jsonify, Response
import subprocess
import requests
import time
import threading

app = Flask(__name__)

# URL of the web server where the video will be sent
server_url = 'http://192.168.1.104:5000/upload_video'  # Change this to your main computer's IP

# Global variable to control streaming
streaming = False

def stream_video():
    global streaming
    # Start capturing video using libcamera-vid and pipe the output
    cmd = ['libcamera-vid', '--inline', '--nopreview', '-o', '-']
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        while streaming:
            # Read the H264 data from stdout
            h264_data = process.stdout.read(1024 * 1024)  # Read in chunks, adjust size if necessary

            if not h264_data:
                print("Failed to grab frame, retrying...")
                time.sleep(0.1)  # Wait before retrying
                continue  # Skip to the next iteration

            # Send the H264 data to the web server
            try:
                # Make sure the content type is set correctly
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
        print("Stream terminated.")

def generate_video_stream():
    # Use libcamera-vid to capture video
    cmd = ['libcamera-vid', '--inline', '--nopreview', '-o', '-']
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        while True:
            # Read video data in chunks
            data = process.stdout.read(1024 * 1024)  # 1 MB chunks
            if not data:
                break
            yield data
    except GeneratorExit:
        process.terminate()
    finally:
        process.terminate()
        print("Video stream terminated.")

@app.route('/start_stream', methods=['POST'])
def start_stream():
    global streaming
    if not streaming:
        streaming = True
        thread = threading.Thread(target=stream_video)
        thread.start()
        return jsonify({"status": "Streaming started"}), 200
    else:
        return jsonify({"status": "Streaming already in progress"}), 400

@app.route('/stop_stream', methods=['POST'])
def stop_stream():
    global streaming
    if streaming:
        streaming = False
        return jsonify({"status": "Streaming stopped"}), 200
    else:
        return jsonify({"status": "Streaming is not active"}), 400

@app.route('/video_stream', methods=['GET'])
def video_stream():
    return Response(generate_video_stream(), content_type='video/h264')

@app.route('/favicon.ico')
def favicon():
    return '', 204  # No Content

# Handle unsupported methods gracefully
@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
