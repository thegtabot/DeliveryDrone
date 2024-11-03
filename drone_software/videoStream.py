import subprocess
import requests
import time
import cv2
import numpy as np

# URL of the web server where the video will be sent
server_url = 'http://<YOUR_MAIN_COMPUTER_IP>:5000/upload_video'  # Change this to your main computer's IP

def stream_video():
    # Start capturing video using libcamera-vid and pipe the output
    cmd = ['libcamera-vid', '--inline', '--nopreview', '--width', '640', '--height', '480', '--framerate', '30']
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    # Read frames from the process output
    while True:
        # Read one frame from stdout
        frame_data = process.stdout.read(640 * 480 * 2)  # Adjusted for YUV format

        if not frame_data:
            print("Failed to grab frame, retrying...")
            time.sleep(0.1)  # Wait before retrying
            continue  # Skip to the next iteration

        # Convert YUV to RGB using OpenCV
        yuv_frame = np.frombuffer(frame_data, dtype=np.uint8).reshape((480, 640, 2))
        frame = cv2.cvtColor(yuv_frame, cv2.COLOR_YUV2BGR_I420)

        # Encode the frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = buffer.tobytes()

        # Send the frame to the web server
        try:
            requests.post(server_url, data=jpg_as_text)
        except Exception as e:
            print(f"Error sending frame: {e}")

        time.sleep(0.1)  # Optional: Add a small delay to limit the frame rate

if __name__ == '__main__':
    stream_video()
