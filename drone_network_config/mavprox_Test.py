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

# Command to connect to the Raspberry Pi via MAVProxy
command = [
    "mavproxy.py", 
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
        # Continuously read and print the output from MAVProxy
        output = process.stdout.readline()
        if output == b"" and process.poll() is not None:
            break
        if output:
            output_str = output.decode("utf-8").strip()
            print(output_str)

            # Check if any pattern matches the output
            for key, pattern in patterns.items():
                match = pattern.search(output_str)
                if match:
                    data[key] = match.group(1)  # Store matched value in the dictionary

        time.sleep(0.1)  # Sleep to avoid maxing out the CPU

except KeyboardInterrupt:
    print("\nScript interrupted. Closing connection...")
    process.terminate()

# Print the extracted data
print("\nExtracted Data:")
for key, value in data.items():
    print(f"{key}: {value}")
