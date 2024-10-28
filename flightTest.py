from dronekit import connect, VehicleMode
import time

# Connect to the Vehicle on UART (GPIO) pins via ttyAMA0
vehicle = connect('/dev/ttyAMA0', baud=57600, wait_ready=True)

def disable_prearm_checks():
    """Disable specific pre-arm checks."""
    print("Disabling pre-arm checks...")
    vehicle.parameters['ARMING_CHECK'] = 0  # Disable all arming checks; use with caution!

def disable_radio_failsafe():
    """Disable radio failsafe parameters."""
    print("Disabling radio failsafe...")
    vehicle.parameters['FS_LOSS_ACTION'] = 0  # 0: No action on loss of radio signal
    vehicle.parameters['FENCE_ENABLE'] = 0  # Disable geofencing

def wait_for_gps_fix():
    """Wait until the vehicle has a GPS fix."""
    while vehicle.gps_0.fix_type < 2:  # Wait for at least a 2D fix
        print("Waiting for GPS fix...")
        time.sleep(1)
    print("GPS fix obtained.")

def arm_and_takeoff(target_altitude):
    """Arms the vehicle and flies to a target altitude."""
    print("Arming motors")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    # Wait until the vehicle is armed
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(target_altitude)

    # Wait until the vehicle reaches a safe altitude before hovering
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        if vehicle.location.global_relative_frame.alt >= target_altitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

# Start the flight test
try:
    # Disable pre-arm checks
    disable_prearm_checks()

    # Disable radio failsafe
    disable_radio_failsafe()

    # Wait for GPS fix
    wait_for_gps_fix()

    # Arm and take off to 1 meter (approximately 3 feet)
    arm_and_takeoff(1)

    print("Hovering for 10 seconds")
    time.sleep(10)  # Hover for 10 seconds

    print("Initiating landing")
    vehicle.mode = VehicleMode("LAND")

    # Wait until the vehicle has landed
    while vehicle.armed:
        print(" Waiting for landing...")
        time.sleep(1)

    print("Landed and disarmed")

finally:
    # Close the vehicle connection
    vehicle.close()
    print("Test completed")
