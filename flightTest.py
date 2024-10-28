from dronekit import connect, VehicleMode
import time

# Connect to the Vehicle via UART GPIO
connection_string = '/dev/ttyAMA0'  # Set to /dev/ttyAMA0 for UART connection
vehicle = connect(connection_string, baud=57600, wait_ready=True)

def disable_failsafes():
    # Disable RC failsafe
    vehicle.parameters['FENCE_ENABLE'] = 0  # Disable geofence
    vehicle.parameters['RC_FAILSAFE'] = 0  # Disable RC failsafe

    # Disable secondary compass failsafe
    vehicle.parameters['COMPASS_USE'] = 0  # Use only the primary compass

def arm_and_takeoff(target_altitude):
    # Wait for the vehicle to initialize
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialize...")
        time.sleep(1)

    # Arm the vehicle
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.arm()

    # Confirm the vehicle is armed
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Vehicle is armed")

    # Take off
    vehicle.simple_takeoff(target_altitude)

    # Wait until the vehicle reaches a safe height
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        if vehicle.location.global_relative_frame.alt >= target_altitude * 0.95:  # 95% of target altitude
            print("Reached target altitude")
            break
        time.sleep(1)

def main():
    target_altitude = 2  # Target altitude in feet
    target_altitude_meters = target_altitude * 0.3048  # Convert feet to meters

    disable_failsafes()  # Disable the failsafes
    arm_and_takeoff(target_altitude_meters)  # Arm and take off to the target altitude

    print("Hovering for 5 seconds...")
    time.sleep(5)  # Hover for 5 seconds

    print("Landing...")
    vehicle.mode = VehicleMode("LAND")  # Switch to land mode

    # Wait until the vehicle lands
    while vehicle.armed:
        print(" Vehicle is still armed, waiting to land...")
        time.sleep(1)

    print("Landed successfully!")

if __name__ == "__main__":
    main()

    # Close vehicle object
    vehicle.close()
