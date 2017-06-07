import time
from dronekit import *
local_simulator = 'localhost:14550'
copter = connect(local_simulator, wait_ready=True)
def arm_and_takeoff(desired_altitude):
    while not copter.is_armable:
        print(" Waiting for copter to initialise...")
        time.sleep(1)
    print("Arming motors")
    copter.mode = VehicleMode("GUIDED")
    copter.armed = True
    while not copter.armed:
        print(" Waiting for arming...")
        time.sleep(1)
    print("Taking off!")
    copter.simple_takeoff(desired_altitude)
    while True:
        print(" Altitude: ", copter.location.global_relative_frame.alt)
        if copter.location.global_relative_frame.alt >= desired_altitude * 0.96:
            print("Reached target altitude")
            break
        time.sleep(1)
arm_and_takeoff(10)
copter.close()
