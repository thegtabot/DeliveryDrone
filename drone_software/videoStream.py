from flask import Flask, Response
import subprocess

app = Flask(__name__)

def generate_video_stream():
    """
    Generate a live video stream from the Raspberry Pi camera with low latency.
    """
    camera_cmd = [
        'libcamera-vid', '--inline', '--nopreview', '--flush',
        '--width', '640', '--height', '480',
        '--framerate', '30', '--timeout', '0', '-o', '-'
    ]

    ffmpeg_cmd = [
        'ffmpeg',
        '-i', '-',  # Input from stdin
        '-c:v', 'libx264',  # H.264 codec
        '-preset', 'ultrafast',  # Minimize encoding time
        '-tune', 'zerolatency',  # Optimize for low latency
        '-g', '30',  # GOP size
        '-f', 'mp4',  # MP4 format
        '-movflags', 'frag_keyframe+empty_moov',  # Web-compatible flags
        '-threads', '2',  # Multi-threading
        'pipe:1'  # Output to stdout
    ]

    try:
        print("Starting camera and FFmpeg processes for live streaming...")
        camera_process = subprocess.Popen(camera_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=camera_process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Stream the output from FFmpeg to the client
        while True:
            frame = ffmpeg_process.stdout.read(1024 * 1024)
            if not frame:
                print("No more frames received from FFmpeg process.")
                break
            yield frame
    except Exception as e:
        print(f"Error during video streaming: {e}")
    finally:
        print("Terminating camera and FFmpeg processes...")
        camera_process.terminate()
        ffmpeg_process.terminate()


@app.route('/video_stream', methods=['GET'])
def video_stream():
    """
    Flask route to serve live video streaming to the client.
    """
    print("Video stream endpoint accessed.")
    return Response(generate_video_stream(), content_type='video/mp4')


if __name__ == '__main__':
    print("Starting Flask application...")
    app.run(host='0.0.0.0', port=5000, threaded=True)
