# *********************************************************#
#   COSGC Presents                                                                                 #
#      __  __________    ________  _____   __    __        #
#     / / / / ____/ /   /  _/ __ \/ ___/   | |  / /        #
#    / /_/ / __/ / /    / // / / /\__ \    | | / /         #
#   / __  / /___/ /____/ // /_/ /___/ /    | |/ /          #
#  /_/ /_/_____/_____/___/\____//____/     |___/           #
#                                                          #
#                                                                                                          #
#  Copyright (c) 2016 University of Colorado Boulder       #
#  COSGC HASP Helios V Team                                                            #
# *********************************************************#


import time
import threading

from adcs import motors_smooth
from adcs import calibrate

# Declare pins
STPA = 29
DRCA = 11
SLPA = 31
STPE = 22
DRCE = 18
SLPE = 32
MS1A = 37
MS2A = 35
MS3A = 33
MS1E = 40
MS2E = 38
MS3E = 36
RSET = 15

# Max steps
az_steps = 12800 # = 360 deg * (4 steps / 1.8 deg) * (16 microsteps / step)
ele_steps = 710 # = 80 deg * (1 step / 1.8 deg) * (16 microsteps / step)
# HELIOS can look 'up' 60 degrees, and 'down' 20 degrees.

# Without Image Analysis, just use diode readings as degrees
movingAvg = 8
a_bias = 0  # Determined experimentally using gnomon
e_bias = 0  # can get more accurate values using image analysis
reading_tol = 1  # Noise in diode readings, needs to be  calculated using diode data
m = 1  # relationship between diode readings and degrees from sun
deg_tol = .25  # minimum number of degrees to move to consider payload centered

# Setting up threading event for whether the reset switch has been hit
switchHit = threading.Event()

def main(downlink, cmd_queue, delev, daz, inhib, camera, nightMode):
    # Set up instances of class
    azimuth = motors_smooth.MotorAZ(STPA, DRCA, MS1A, MS2A, MS3A)
    elevation = motors_smooth.MotorELE(STPE, DRCE, MS1E, MS2E, MS3E, RSET, switchHit)

    cali = calibrate.calibrate(camera)

    #initialize variables
    panning = False
    loop_time = 0
    run_anly = True

    az_reading = 0
    ele_reading = 0
    azArray = [0]
    eleArray = [0]

    anly_tolerance = 3.5

    downlink.put(["AD", "BU", "ADCS"]) # Bootup message

    while True:  # Flight loop
        while not cmd_queue.empty():  # Command Handling
            cmd = cmd_queue.get()
            if type(cmd) is bytes:
                packet = hex(int.from_bytes(cmd, byteorder='big'))
                # Turn on panning
                if cmd == b"\xFA":
                    panning = True
                    downlink.put(["AD", "AC", packet])
                # Turn off panning
                elif cmd == b"\xFB":
                    panning = False
                    downlink.put(["AD", "AC", packet])
                # Toggle elevation diodes
                elif cmd == b"\xA1":
                    success = False
                    while not success:
                        try:
                            daz.switch()
                            success = True
                        except:
                            pass
                    time.sleep(1. / 6.)
                    downlink.put(["AD", "AC", packet])
                # Toggle azimuth diodes
                elif cmd == b"\xA0":
                    success = False
                    while not success:
                        try:
                            delev.switch()
                            success = True
                        except:
                            pass
                    time.sleep(1. / 6.)
                    downlink.put(["AD", "AC", packet])
                # Turn on image analysis
                elif cmd == b"\xB1":
                    run_anly = True
                    downlink.put(["AD", "AC", packet])
                # Turn off image analysis
                elif cmd == b"\xB0":
                    run_anly = False
                    downlink.put(["AD", "AC", packet])
                # Night mode on/off
                elif cmd == b"\xD0":
                    nightMode.clear()
                elif cmd == b"\xD1":
                    nightMode.set()
                elif cmd == b"\xBF": # Reset function
                    elevation.resetCount()
                    downlink.put(["AD", "SW", "RSET"])
                    # Implement reset fxn call
                else:
                    downlink.put(["AD", "ER", packet])
            # Nudge
            elif type(cmd) is int:
                packet = cmd
                downlink.put(["AD", "AC", str(cmd)])
                # Nudge azimuth
                if -180 <= cmd <= 180:
                    azimuth.turnStep(cmd, True, False)
                    downlink.put(["AD", "AC", str(cmd)])
                # Nudge elevation
                elif cmd <= -180:
                    cmd += 180
                    elevation.turnStep(cmd, True, False)
                    downlink.put(["AD", "AC", str(cmd)])
                elif cmd >= 180:
                    cmd -= 180
                    elevation.turnStep(cmd, True, False)
                    downlink.put(["AD", "AC", str(cmd)])
                else:
                    downlink.put(["AD", "ER", str(cmd)])

        if switchHit.is_set():
            downlink.put(["AD", "SW", "HIT"])
            print("STEVE HAS BEEN TURNED ON")
            # Thank Haleigh for the above
            # Steve is the switch's name
            switchHit.clear()

        if panning:
            # azimuth.wait = 0.0008
            azimuth.move(64)  # make sure this is greater than the tolerance!
            # time.sleep(0.22)
            if azimuth.cnt >= az_steps: # Went more than 360 deg
                azimuth.move(-azimuth.cnt)
                if elevation.cnt <= ele_steps - (10 / .1125):
                    elevation.move(-10 / 0.1125)
                else:
                    elevation.move(elevation.cnt)

        elif nightMode.is_set(): # Short code = best code.  :)
            print("Night mode is ON")
            continue

        else:  # MAIN FLIGHT LOOP
            loop_time += 1. / 6.
            try:
                # Take azimuth diode reading
                az_reading = daz.read()
            except:
                pass
            try:
                # Take elevation diode reading
                ele_reading = delev.read()
            except:
                pass

            # Moving average filter

            # Add new reading to moving average
            eleArray.append(ele_reading)
            azArray.append(az_reading)

            # Remove old reading from moving average
            azArray.pop(0)
            eleArray.pop(0)

            # Find the average
            total_ele = sum(eleArray)
            total_az = sum(azArray)
            readA = (total_az / movingAvg) + a_bias
            readE = (total_ele / movingAvg) + e_bias

            if run_anly: # If image analysis is turned on
                if abs(readA) < anly_tolerance and abs(readE) < anly_tolerance: # When the sun should be in the FOV
                    ret, move_az, move_ele = cali.analyze()
                else:
                    ret = 0
            else:
                ret = 0

            if ret == 1:
                # The sun is in the FOV, so move off of image analysis
                degA = move_az
                degE = move_ele
                anly = True
            else:
                # The sun is not in the FOV, so move off of diode readings
                degA = readA
                degE = readE
                anly = False

            # Downlink results
            if loop_time >= 1. / 3.:
                if anly:
                    downlink.put(["AD", "AN", "%i, %f, %f" % (ret, degA, degE)])
                downlink.put(["AD", "DI", "%f, %f" % (degA, degE)])
                downlink.put(["AD", "MC", "%i %i, %i %i" % (azimuth.cnt, (azimuth.cnt*12800/360), elevation.cnt, (elevation.cnt*528/80))])
                loop_time = 0

            # Turn based on degrees
            # The sleep time is necessary to prevent the diodes from trying to sample faster than they are able
            if not inhib: # If the "Remove Before Flight" pin is not activated
                if abs(degA) > deg_tol: # If azimuth reading is outside the tolerance
                    azimuth.turnStep(degA, False, anly) # Turn the azimuth motor
                else:
                    time.sleep(.025)
                if abs(degE) > deg_tol: # If elevation reading is outside the tolerance
                    elevation.turnStep(degE, False, anly) # Turn the elevation motor
                else:
                    time.sleep(.025)
            if inhib: # If the "Remove Before Flight" pin is activated, don't turn
                time.sleep(1. / 15.)
