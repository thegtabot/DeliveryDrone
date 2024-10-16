from dronekit import Command, LocationGlobalRelative


def navigate_to(lat, lon, alt)
    cmds = vehicle.commands
    cmds.clear()

    # Add multiple waypoints
    deliveryStack = [
        [lat, lon, alt]  # Delivery points append here
                             # Add more waypoints as needed
    ]

    for lat, lon, alt in deliveryStack:
        wp = Command(0, 0, 0, Command.WAYPOINT, 0, 0, 0, 0, 0, 0, lat, lon, alt)
        cmds.add(wp)

    cmds.upload()
    vehicle.mode = VehicleMode("AUTO")
