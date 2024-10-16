from dronekit import Command, LocationGlobalRelative


def navigate_to(coords)
    cmds = vehicle.commands
    cmds.clear()

    # Add waypoints
    deliveryStack = []
         # Delivery points append here              
         # Add more waypoints as needed

    deliveryStack.append(coords)
    
    #0 is lat 
    #1 is lon
    #2 is alt
    for deliveryStack[0], deliveryStack[1], deliveryStack[2] in deliveryStack: 
        wp = Command(0, 0, 0, Command.WAYPOINT, 0, 0, 0, 0, 0, 0, deliveryStack[0], deliveryStack[1], deliveryStack[2])
        cmds.add(wp)

    cmds.upload()
    vehicle.mode = VehicleMode("AUTO")

'''
from dronekit import VehicleMode, LocationGlobalRelative

# Set the vehicle to GUIDED mode for autonomous control
vehicle.mode = VehicleMode("GUIDED")

# Define the target GPS coordinates (latitude, longitude, altitude)
target_location = LocationGlobalRelative(latitude, longitude, altitude)

# Command the drone to fly to the target location
vehicle.simple_goto(target_location)
'''