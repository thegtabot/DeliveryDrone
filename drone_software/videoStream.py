import cv2
import requests
import time
import numpy as np

# URL of the web server where the video will be sent
server_url = 'http://10.0.0.1:5000/upload_video'  # Change this to your main computer's IP

def stream_video():
    # Initialize the camera
    cap = cv2.VideoCapture(0)  # Use 0 for the Pi camera

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Encode the frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = buffer.tobytes()

        # Send the frame to the web server
        try:
            requests.post(server_url, data=jpg_as_text)
        except Exception as e:
            print(f"Error sending frame: {e}")

        # Optional: Add a small delay to limit the frame rate
        time.sleep(0.1)

    cap.release()

if __name__ == '__main__':
    stream_video()
