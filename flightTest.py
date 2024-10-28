from dronekit import connect, VehicleMode
import time

# Connect to the Vehicle on UART (GPIO) pins via ttyAMA0
vehicle = connect('/dev/ttyAMA0', baud=57600, wait_ready=True)  # Adjust baud rate if necessary

def disable_prearm_checks():
    """Disable specific pre-arm checks."""
    print("Disabling pre-arm checks...")

    # Disable GPS checks
    vehicle.parameters['GPS_AUTO_SWITCH'] = 1  # Set to 1 to auto-switch GPS sources if multiple are available
    vehicle.parameters['GPS_TYPE'] = 1  # Set to use the GPS type you are using (if applicable)

    # Disable compass checks
    vehicle.parameters['COMPASS_USE2'] = 0  # Disable Compass 2
    vehicle.parameters['COMPASS_ORIENT'] = 0  # Use default orientation if needed

    # Disable altitude checks (optional)
    vehicle.parameters['ARMING_CHECK'] = 0  # Disable all arming checks; use with caution!

    # Verify changes
    print("GPS_AUTO_SWITCH set to:", vehicle.parameters['GPS_AUTO_SWITCH'])
    print("COMPASS_USE2 set to:", vehicle.parameters['COMPASS_USE2'])
    print("ARMING_CHECK set to:", vehicle.parameters['ARMING_CHECK'])

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
