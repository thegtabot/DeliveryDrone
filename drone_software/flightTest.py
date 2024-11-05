from dronekit import connect, VehicleMode
import time

# Connect to the Vehicle via UART GPIO
connection_string = '/dev/ttyAMA0'
vehicle = connect(connection_string, baud=57600, wait_ready=True, timeout=30)

def disable_failsafes():
    print("Disabling failsafes...")
    try:
        vehicle.parameters['RC_FAILSAFE'] = 0
    except Exception as e:
        print(f"Error disabling RC_FAILSAFE: {e}")
    try:
        vehicle.parameters['FS_OPTIONS'] = 0
    except Exception as e:
        print(f"Error disabling FS_OPTIONS: {e}")
    try:
        vehicle.parameters['COMPASS_USE'] = 0
    except Exception as e:
        print(f"Error disabling COMPASS_USE: {e}")
    try:
        vehicle.parameters['ARMING_CHECK'] = 0
    except Exception as e:
        print(f"Error disabling ARMING_CHECK: {e}")

def arm_and_takeoff(target_altitude):
    # Set GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    while vehicle.mode.name != "GUIDED":
        print(" Waiting for mode change to GUIDED...")
        time.sleep(1)

    # Wait for vehicle to become armable
    while not vehicle.is_armable:
        print(f"Waiting for vehicle to initialize. Status: {vehicle.system_status.state}")
        time.sleep(1)

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

def main():
    target_altitude_ft = 3
    target_altitude_m = target_altitude_ft * 0.3048  # Convert feet to meters

    disable_failsafes()
    arm_and_takeoff(target_altitude_m)

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
