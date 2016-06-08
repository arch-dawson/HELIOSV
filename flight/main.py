# *********************************************************#
#   COSGC Presents										   #
#      __  __________    ________  _____   __    __        #
#     / / / / ____/ /   /  _/ __ \/ ___/   | |  / /        #
#    / /_/ / __/ / /    / // / / /\__ \    | | / /         #
#   / __  / /___/ /____/ // /_/ /___/ /    | |/ /          #
#  /_/ /_/_____/_____/___/\____//____/     |___/           #  
#                                                          #
#   													   #
#  Copyright (c) 2016 University of Colorado Boulder	   #
#  COSGC HASP Helios V Team							       #
# *********************************************************#


import threading
import queue

# Set up GPIO pin for motor inhibit
import RPi.GPIO as gpio
gpio.setwarnings(False)
gpio.setmode(gpio.BOARD)


def shutdown():
    """ Completes all necessary events for a shutdown """
    camera.close()
    exit()

# Import code for threading. All flight code must be initialized from the main function in the thread file
from adcs import adcs
from sens import sens
from uplk import uplk
from dwnl import dwnl
from serv import serv

# Directory for all code shared between threads
from shared import i2c
from shared import diodes
from shared import easyserial
from shared import camera

# Create required Queues
adcs_cmd = queue.Queue()
capt_cmd = queue.Queue()
sens_cmd = queue.Queue()
downlink = queue.Queue()
inputQ = queue.Queue()

# Create shared photodiode, serial buses, cameras, and default model
i2c_bus = i2c.I2Cbus()
ele = diodes.Bus('e', i2c_bus)
azi = diodes.Bus('a', i2c_bus)
gnd_bus = easyserial.Bus("/dev/ttyAMA0", 4800)
camera = camera.Camera(0)

# Check if the inhibit is active and set ADCS flag if it is.
inhibit = 12
gpio.setup(inhibit, gpio.IN)
motorInhibit = True if gpio.input(inhibit) else False

# Setting up nightMode event as a flag to be seen across threads
# Event is like global boolean but safer for multithreading
nightMode = threading.Event()

# Package arg tuples for thread
dwnl_args = (downlink, gnd_bus)
uplk_args = (downlink, gnd_bus, adcs_cmd, sens_cmd, inputQ, nightMode) # Implement nightMode here
sens_args = (downlink, i2c_bus, camera, sens_cmd)
adcs_args = (downlink, adcs_cmd, ele, azi, motorInhibit, camera, nightMode)
serv_args = (downlink, inputQ, nightMode)

# Create thread objects
threads = [
    threading.Thread(name='dwnl', target=dwnl.main, args=dwnl_args),
    threading.Thread(name='uplk', target=uplk.main, args=uplk_args),
    threading.Thread(name='sens', target=sens.main, args=sens_args),
    threading.Thread(name='adcs', target=adcs.main, args=adcs_args),
    threading.Thread(name='serv', target=serv.main, args=serv_args)
]


# Start running threads within a try-except block to allow for it to catch exceptions
try:
    for t in threads:
        t.daemon = True  # Prevents it from running without main
        t.start()
    while True:
        for t in threads:
            t.join(5)  # Prevent main from quitting by joining threads
except(KeyboardInterrupt, SystemExit):
    # Capture an exit condition and shut down the flight code
    shutdown()
