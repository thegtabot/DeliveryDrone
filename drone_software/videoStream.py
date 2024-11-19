import subprocess
import requests
import time

# URL of the web server where the video will be sent
server_url = 'http://10.0.0.1:5000/upload_video'  # Change this to your main computer's IP

def stream_video():
    # Start capturing video using libcamera-vid and pipe the output
    cmd = ['libcamera-vid', '--inline', '--nopreview', '-o', '-']
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        while True:
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

    except KeyboardInterrupt:
        print("Terminating video stream...")
        process.terminate()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        process.terminate()
        print("Stream terminated.")

if __name__ == '__main__':
    stream_video()
