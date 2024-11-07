import subprocess
import time
import re

# Replace with the IP and port for the Raspberry Pi
raspberry_pi_ip = "10.0.0.1"
mavproxy_port = "14550"  # This is usually the port MAVProxy listens on (adjust if different)

# Regular expression patterns to capture relevant output
patterns = {
    "APM_Copter_version": re.compile(r"APM:Copter (\S+)"),
    "PX4_version": re.compile(r"PX4: (\S+)"),
    "Frame_type": re.compile(r"Frame: (\S+)"),
    "PX4_hardware_version": re.compile(r"PX4v3 (\S+)"),
}

# Command to run MAVProxy with the correct path to mavproxy.py in the virtual environment
command = [
    "wsl", "python3", "/mnt/c/Users/gtas3/Desktop/DeliveryDrone/DeliveryDrone/.venv/Scripts/mavproxy.py",  # Use full path to mavproxy.py
    "--master", f"udp:{raspberry_pi_ip}:{mavproxy_port}",
    "--out", "udp:0.0.0.0:14551",  # Example for the output (you can change it as needed)
    "--logfile", "mavproxy_log.txt",  # Optional: log the output to a file
]

# Start MAVProxy connection
print(f"Connecting to MAVProxy at {raspberry_pi_ip}:{mavproxy_port}...")
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Initialize dictionary to hold the parsed information
data = {
    "APM_Copter_version": None,
    "PX4_version": None,
    "Frame_type": None,
    "PX4_hardware_version": None,
}

# Output from the MAVProxy
try:
    while True:
        # Continuously read and print the output from
