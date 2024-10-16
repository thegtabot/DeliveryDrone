from dronekit import connect, VehicleMode
import time

# Connect to the vehicle (replace '127.0.0.1:14550' with your drone's connection string)
# For Pixhawk over USB, you can use '/dev/ttyUSB0', 115200 for the baudrate.
vehicle = connect('/dev/ttyAMA0', wait_ready=True,heartbeat_timeout=60)

def print_telemetry():
    while True:
        # Print GPS info
        print(f"GPS: {vehicle.gps_0}")
        
        # Print Global Location
        print(f"Global Location (Lat, Lon): {vehicle.location.global_frame}")
        
        # Print Attitude (Pitch, Roll, Yaw)
        print(f"Attitude: {vehicle.attitude}")
        
        # Print Velocity
        print(f"Velocity: {vehicle.velocity}")
        
        # Print Airspeed
        print(f"Airspeed: {vehicle.airspeed}")
        
        # Print Battery info
        print(f"Battery: {vehicle.battery}")
        
        # Print EKF Status
        print(f"EKF OK?: {vehicle.ekf_ok}")
        
        # Print the current mode
        print(f"Mode: {vehicle.mode.name}")
        
        # Print Arm Status
        print(f"Armed: {vehicle.armed}")
        
        print("------------------------------------------------------------")
        time.sleep(1)  # Delay for readability and to avoid overloading the system

# Call the function to print telemetry
print_telemetry()

# Close the vehicle connection before exiting the script
vehicle.close()
