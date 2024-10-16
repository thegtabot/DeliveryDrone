from dronekit import Command, LocationGlobalRelative


def navigate_to(lat, lon, alt)
    cmds = vehicle.commands
    cmds.clear()

    # Add multiple waypoints
    waypoints = [
        (lat1, lon1, alt),  # First delivery point
        (lat2, lon2, alt2),  # Second delivery point
        # Add more waypoints as needed
    ]

    for lat, lon, alt in waypoints:
        wp = Command(0, 0, 0, Command.WAYPOINT, 0, 0, 0, 0, 0, 0, lat, lon, alt)
        cmds.add(wp)

    cmds.upload()
    vehicle.mode = VehicleMode("AUTO")
