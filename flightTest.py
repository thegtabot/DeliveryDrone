from dronekit import connect, VehicleMode
import time

# Connect to the Vehicle via UART GPIO
connection_string = '/dev/ttyAMA0'  # Set to /dev/ttyAMA0 for UART connection
vehicle = connect(connection_string, baud=57600, wait_ready=True)

def disable_failsafes():
    try:
        vehicle.parameters['FENCE_ENABLE'] = 0  # Disable geofence
    except Exception as e:
        print(f"Error disabling FENCE_ENABLE: {e}")
    try:
        vehicle.parameters['RC_FAILSAFE'] = 0  # Disable RC failsafe
    except Exception as e:
        print(f"Error disabling RC_FAILSAFE: {e}")
    try:
        vehicle.parameters['FS_OPTIONS'] = 0 
    except Exception as e:
        print(f"Error disabling FS_OPTIONS: {e}")
    try:
        vehicle.parameters['COMPASS_USE'] = 0  # Use only the primary compass
    except Exception as e:
        print(f"Error disabling COMPASS_USE: {e}")

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

        # Re-enable failsafe parameters
    vehicle.parameters['FS_THR_ENABLE'] = 1  # Enable throttle failsafe
    vehicle.parameters['FS_OPTIONS'] = 1      # Enable all failsafe options
    vehicle.parameters['NAV_RCL_ACT'] = 1     # Enable return to launch on radio failsafe

    vehicle.flush()


    print("Landed successfully!")

    

if __name__ == "__main__":
    main()

    # Close vehicle object
    vehicle.close()
