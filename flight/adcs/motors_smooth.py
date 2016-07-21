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
import math

import RPi.GPIO as gpio
import numpy as np
import threading

reading_tol = 1  # Noise in diode readings, needs to be calculated using diode data
m = 1  # Relationship between diode readings and degrees off from sun, needs to be calculated
deg_tol = .5  # Min number of degrees to turn so that payload is considered centered

diode_wait = .1
WaitTime = 0.0024
aziMaxStep = 1.8 / 4 # 1.8 deg per step, four-to-one gear ratio
eleMaxStep = 1.8 # 1.8 deg per step, one-to-one gear ratio

az_steps = 12800 # 12800 steps on azimuth is equal to 360 deg
ele_steps = 500  # 710 steps on elevation is equal to about 80 deg (max height of elevation)

gpio.setwarnings(False)
gpio.setmode(gpio.BOARD)


class MotorAZ: # Azimuth motor
    def __init__(self, stp, drc, ms1, ms2, ms3):
        self.stp = stp
        gpio.setup(stp, gpio.OUT)
        self.drc = drc
        gpio.setup(drc, gpio.OUT)
        self.ms1 = ms1
        gpio.setup(ms1, gpio.OUT)
        self.ms2 = ms2
        gpio.setup(ms2, gpio.OUT)
        self.ms3 = ms3
        gpio.setup(ms3, gpio.OUT)
        self.cnt = 0
        self.microsteps = 16
        self.wait = WaitTime
        self.lock = threading.Lock()
        self.k = 1
        gpio.output(self.ms1, ms1)
        gpio.output(self.ms2, ms2)
        gpio.output(self.ms3, ms3)

    # Function to turn the motors
    def turnStep(self, deg, blocking, anly):
        if blocking: # If a nudge command was sent
            # Determine number of steps to take to moved desired number of degrees
            steps = deg / (aziMaxStep / self.microsteps)
            self.wait = .0008
            if abs(self.cnt + steps) > az_steps: # If the nudge would send it over 360 degrees
                if self.cnt < 0: # If -360 degrees, move +360 degrees to get to zero
                    new_pos = (steps + self.cnt) + az_steps
                elif self.cnt > 0: # If +360 degrees, move -360 degrees to get to zero
                    new_pos = (steps + self.cnt) - az_steps
                # Actually move the motor
                self.move(new_pos - self.cnt)
                steps = 0

        else: # If a nudge command has not been sent
            if anly: # If image analysis is turned on
                # Determine number of steps to take to moved desired number of degrees
                steps = (np.sign(deg) * self.microsteps * deg_tol / aziMaxStep) / 2
            else: # If image analysis is turned off
                # Determine number of steps to take to moved desired number of degrees
                steps = np.sign(deg) * self.microsteps * deg_tol / aziMaxStep
            if steps:
                if anly:
                    self.wait = (diode_wait / abs(steps)) / 4
                else:
                    self.wait = (diode_wait / abs(steps))
        if abs(deg) >= .15: #changed 7/21 deg_tol: # If outside the tolerance
            if abs(self.cnt) < az_steps: # If it hasn't moved 360 degrees around
                self.move(steps)
            else: # If it's reached 360 degrees
                self.wait = 0.0008
                self.move(-self.cnt) # Move back to zero
        else:
            time.sleep(diode_wait / 2)

    # TurnStep uses this function to actually move the motor
    def move(self, steps):
        steps = math.floor(steps)
        # Determine if you're moving clockwise or counterclockwise
        if steps > 0:
            drc = True
        elif steps < 0:
            drc = False
        else:
            return
        # Turn the number of steps desired
        for i in range(abs(steps)):
            gpio.output(self.drc, drc)
            gpio.output(self.stp, True)
            gpio.output(self.stp, False)
            time.sleep(self.wait)
        # Record how man steps you've turned
        self.cnt += steps * (16 / self.microsteps)


class MotorELE: # Similar to previous class but for elevation motor instead of azimuth motor
    def __init__(self, stp, drc, ms1, ms2, ms3, rset, switchHit):
        self.stp = stp
        gpio.setup(stp, gpio.OUT)
        self.drc = drc
        gpio.setup(drc, gpio.OUT)
        self.ms1 = ms1
        gpio.setup(ms1, gpio.OUT)
        self.ms2 = ms2
        gpio.setup(ms2, gpio.OUT)
        self.ms3 = ms3
        gpio.setup(ms3, gpio.OUT)
        self.rset = rset
        gpio.setup(rset, gpio.IN)
        self.cnt = 0
        self.microsteps = 16   # This line shall forever be doomed to the lowest pit of hell
        self.wait = diode_wait / self.microsteps
        self.switchHit = switchHit
        gpio.output(self.ms1, ms1)
        gpio.output(self.ms2, ms2)
        gpio.output(self.ms3, ms3)

    def turnStep(self, deg, blocking, anly):
        if blocking: # If nudge
            steps = deg / (eleMaxStep / self.microsteps)
            self.wait = diode_wait / self.microsteps
            # If nudging would put elevation too high or low
            if -steps + self.cnt > ele_steps: # If nudging would put elevation too high
                steps = -ele_steps + self.cnt
            elif -steps + self.cnt < 0: # If nudging would put elevation too low
                steps = self.cnt
        else:
            if anly:
                steps = (np.sign(deg) * self.microsteps * deg_tol / eleMaxStep) / 2
            else:
                steps = np.sign(deg) * self.microsteps * deg_tol / eleMaxStep
            if steps:
                if anly:
                    self.wait = (diode_wait / abs(steps)) / 4
                else:
                    self.wait = (diode_wait / abs(steps))
        if abs(deg) >= .15: # changed 7/21 deg_tol:
            if self.cnt >= 0:
                if self.cnt < ele_steps:
                    self.move(steps)
                elif self.cnt >= ele_steps and steps > 0:
                    self.move(steps)
                else:
                    time.sleep(diode_wait / 2)

            elif self.cnt < 0 and steps < 0:
                self.move(steps)
            else:
                time.sleep(diode_wait / 2)
        else:
            time.sleep(diode_wait / 2)

    def panStep(self):
        # Have an alternate version of flight code in case the diodes aren't working
        # This just steps the elevation 10 degrees 
        # ele_steps = 710
        # self.cnt = motor count
        # Resets to ele_steps at switch 
        turn = math.ceil(self.cnt * (1.8 / 16))
        if self.cnt: # If motor count is greater than 0
            self.turnStep(min(1, turn) , True, False)
        else:
            self.turnStep(-ele_steps, True, False)
        return

    def checkSwitch(self, drc): # Return true if switch has been hit
        if gpio.input(self.rset):
            self.cnt = ele_steps 
            if not self.switchHit.is_set():
                self.switchHit.set()
        return self.switchHit.is_set() and (drc == False)
    # Still want to be able to turn AWAY from switch.

    def resetCount(self):
        drc = False # Direction is UP
        count = 0
        ele_deg = ele_steps * ( 1.8 / 16) * 1.5
        while not self.checkSwitch(drc) and count < ele_deg:
            self.turnStep(-1, True, False) 
            count += 1
        self.move(2)
        return

    def move(self, steps):
        steps = math.floor(steps)
        if steps < 0: # Up
            drc = False
            self.cnt += -steps * (16 / self.microsteps) 
        elif steps > 0: # Down
            drc = True
            self.cnt += -steps * (16 / self.microsteps)
        else:
            return
        for i in range(abs(steps)):
            if self.checkSwitch(drc):
                break
            gpio.output(self.drc, drc) # Direction
            gpio.output(self.stp, True)
            gpio.output(self.stp, False)
            time.sleep(self.wait) #self.wait
