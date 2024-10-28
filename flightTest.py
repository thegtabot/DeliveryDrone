from dronekit import connect, VehicleMode
import time

# Connect to the Vehicle on UART (GPIO) pins via ttyAMA0
vehicle = connect('/dev/ttyAMA0', baud=57600, wait_ready=True)  # Adjust baud rate if necessary

def arm_and_takeoff(target_altitude):
    """
    Arms the vehicle and flies to a target altitude.
    """
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
        # Break and hover at the target altitude
        if vehicle.location.global_relative_frame.alt >= target_altitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

# Start the flight test
try:
    # Arm and take off to 1 meter (approximately 3 feet)
    arm_and_takeoff(1)

    print("Hovering for 10 seconds")
    time.sleep(10)

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
