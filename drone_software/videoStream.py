import subprocess

def stream_video():
    # This command will start the libcamera-vid command for video streaming
    cmd = ['libcamera-vid', '--output', 'video.h264', '--width', '640', '--height', '480', '--framerate', '30']
    subprocess.run(cmd)

if __name__ == '__main__':
    stream_video()
