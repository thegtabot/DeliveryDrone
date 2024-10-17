from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import socket
#import exceptions
import math
import argparse

######Func#####

def connectMyCopter():
    parser= argparse.ArgumentParser(description='commands')
    parser.add_argument('--connect')
    args = parser.parse_args()

    connection_string = args.connect
    baud_rate = 57600

    vehicle = connect(connection_string, baud=baud_rate, wait_ready=True)
    return vehicle

def arm():
    while vehicle.is_armable == False:
        print('Waiting for vehicle to become armable..')
        time.sleep(1)
        print("")
    
    print("Vehicle can be armed.")
    vehicle.armed = True

    while vehicle.armed == False:
        print("Waiting for drone to become armed...")
        time.sleep(2)
    return None

vehicle = connectMyCopter()
arm()