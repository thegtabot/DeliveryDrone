from dronekit import connect, VehicleMode
import time

# Connect to the Vehicle via UART GPIO
connection_string = '/dev/ttyAMA0'
vehicle = connect(connection_string, baud=57600, wait_ready=True, timeout=30)

def disable_failsafes():
    print("Disabling failsafes...")
    failsafe_params = {
        'RC_FAILSAFE': 0,
        'FS_OPTIONS': 0,
        'COMPASS_USE': 0,
        'ARMING_CHECK': 0
    }
    for param, value in failsafe_params.items():
        try:
            vehicle.parameters[param] = value
            print(f"Set {param} to {value}")
            time.sleep(1)  # Add a delay to ensure parameters are set
        except Exception as e:
            print(f"Error setting {param}: {e}")

def arm_and_takeoff(target_altitude):
    # Set GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    while vehicle.mode.name != "GUIDED":
        print(" Waiting for mode change to GUIDED...")
        time.sleep(1)

    # Wait for vehicle to become armable with a timeout
    start_time = time.time()
    while not vehicle.is_armable:
        print(f"Waiting for vehicle to initialize. Status: {vehicle.system_status.state}")
        time.sleep(1)
        if time.time() - start_time > 30:  # Timeout after 30 seconds
            print("Vehicle is not armable. Check sensors and parameters.")
            return False

    # Arm the vehicle
    vehicle.armed = True
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Vehicle is armed. Taking off!")

    # Take off
    vehicle.simple_takeoff(target_altitude)

    # Wait until the vehicle reaches a safe height
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        if vehicle.location.global_relative_frame.alt >= target_altitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)
    return True

def main():
    target_altitude_ft = 3
    target_altitude_m = target_altitude_ft * 0.3048  # Convert feet to meters

    disable_failsafes()
    if not arm_and_takeoff(target_altitude_m):
        print("Takeoff aborted due to initialization failure.")
        return

    print("Hovering for 10 seconds...")
    time.sleep(10)

    print("Landing...")
    vehicle.mode = VehicleMode("LAND")
    while vehicle.armed:
        print(" Vehicle is still armed, waiting to land...")
        time.sleep(1)

    # Re-enable failsafes
    vehicle.parameters['FS_THR_ENABLE'] = 1
    vehicle.parameters['FS_OPTIONS'] = 1
    vehicle.parameters['NAV_RCL_ACT'] = 1

    print("Landed successfully!")

if __name__ == "__main__":
    main()
    vehicle.close()
