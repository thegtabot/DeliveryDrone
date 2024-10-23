from dronekit import connect, VehicleMode, LocationGlobalRelative
import time

def send_gps_target_to_drone(lat, lon, alt, connection_str='/dev/serial0', baudrate=57600):
    """
    Sends a command to the drone to fly to a specific GPS coordinate.
    
    :param lat: Latitude in decimal degrees
    :param lon: Longitude in decimal degrees
    :param alt: Altitude in meters relative to home position
    :param connection_str: MAVLink connection string (default: '/dev/serial0' for Pixhawk on Raspberry Pi)
    :param baudrate: Connection baudrate (default: 57600)
    """
    
    # Connect to the Pixhawk via serial
    print(f"Connecting to Pixhawk on {connection_str} with baudrate {baudrate}...")
    vehicle = connect(connection_str, baud=baudrate, wait_ready=True)
    
    # Function to arm and takeoff the drone to a specific altitude
    def arm_and_takeoff(target_altitude):
        print("Arming motors")
        
        # Set mode to GUIDED
        vehicle.mode = VehicleMode("GUIDED")
        vehicle.armed = True

        # Wait until the vehicle is armed
        while not vehicle.armed:
            print("Waiting for arming...")
            time.sleep(1)

        print("Taking off!")
        vehicle.simple_takeoff(target_altitude)

        # Wait until the vehicle reaches the target altitude
        while True:
            print(f"Altitude: {vehicle.location.global_relative_frame.alt}")
            if vehicle.location.global_relative_frame.alt >= target_altitude * 0.95:  # Target altitude reached
                print("Reached target altitude")
                break
            time.sleep(1)

    # Arm the drone and takeoff to the specified altitude
    arm_and_takeoff(alt)

    # Command the drone to fly to the specified GPS coordinates
    print(f"Navigating to target coordinates: Lat={lat}, Lon={lon}, Alt={alt}")
    point = LocationGlobalRelative(lat, lon, alt)
    vehicle.simple_goto(point)

    # Wait for 30 seconds or until the drone reaches the destination
    time.sleep(30)

    # Optionally, you can monitor the drone’s current location
    while True:
        current_location = vehicle.location.global_relative_frame
        print(f"Current position: Lat: {current_location.lat}, Lon: {current_location.lon}, Alt: {current_location.alt}")
        
        # Check if the drone has arrived within a small threshold
        if abs(current_location.lat - lat) < 0.00001 and abs(current_location.lon - lon) < 0.00001:
            print("Reached the target location.")
            break
        
        time.sleep(1)

    # Land the vehicle after reaching the target
    print("Landing...")
    vehicle.mode = VehicleMode("LAND")

    # Close vehicle connection
    vehicle.close()
    print("Connection closed.")

# Example usage
# Replace with your target GPS coordinates
target_lat = 38.897957   # Example: White House latitude
target_lon = -77.036560  # Example: White House longitude
target_alt = 20          # Example: 20 meters altitude

# Send the drone to the GPS coordinates
send_gps_target_to_drone(target_lat, target_lon, target_alt)
