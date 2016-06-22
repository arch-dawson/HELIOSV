#*********************************************************#
#   COSGC Presents                                                                                #
#      __  __     ___               ____________                  #
#     / / / /__  / (_)___  _____   /  _/  _/  _/                  #
#    / /_/ / _ \/ / / __ \/ ___/   / / / / / /                    #
#   / __  /  __/ / / /_/ (__  )  _/ /_/ /_/ /                     #
#  /_/ /_/\___/_/_/\____/____/  /___/___/___/                     #
#                                                                                                         #
#  Copyright (c) 2014 University of Colorado Boulder      #
#  COSGC HASP Helios III Team                                                     #
#*********************************************************#

import threading
import logging
import queue


import time
import RPi.GPIO as gpio

WaitTime = 0.0024

class MotorAZ():
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
        self.microsteps = 8

    def setStep(self, deg):
        #setting microsteps based on how far away the camera is from the sun
        if abs(deg) >= 1.8:
            ms1, ms2, ms3 = False
            self.microsteps = 1

        elif abs(deg) >= 0.9:
            ms1 = True
            ms2, ms3 = False
            self.microsteps = 2

        elif abs(deg) >= 0.45:
            ms1, ms3 = False
            ms2 = True
            self.microsteps = 4

        elif abs(deg) >= 0.225:
            ms1, ms2 = True
            ms3 = False
            self.microsteps = 8

        else:
            ms1, ms2, ms3 = False
            self.microsteps = 16

        gpio.output(self.ms1, ms1)
        gpio.output(self.ms2, ms2)
        gpio.output(self.ms3, ms3)

    def turnStep(self, deg):
        tolerance = .1125 # min degrees per step (verify with gear ratio)
        self.setStep(deg)
        if deg > tolerance:
            if cnt < az_steps:
                self.move(1)
            else:
                self.setStep(2) #sets it to full steps
                self.move(-self.cnt)

        if deg < -tolerance:
            if cnt > -az_steps:
                self.move(-1)
            else:
                self.setStep(2) #sets it to full steps
                self.move(-self.cnt)  # moves 200 full steps back to origin


    def move(self, steps)
        if steps > 0:
            drc = True
            self.cnt += steps*(16 / self.microsteps)
        elif steps < 0:
            drc = False
            self.cnt -= steps*(16 / self.microsteps)
        else:
            return
        for i in range(abs(steps)):
            gpio.output(self.drc, drc)
            gpio.output(self.stp, True)
            gpio.output(self.stp, False)
            time.sleep(WaitTime)

class MotorELE():
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
        self.microsteps = 8

    def setStep(self, deg):
        #setting microsteps based on how far away the camera is from the sun
        if abs(deg) >= 1.8:
            ms1, ms2, ms3 = False
            self.microsteps = 1

        elif abs(deg) >= 0.9:
            ms1 = True
            ms2, ms3 = False
            self.microsteps = 2

        elif abs(deg) >= 0.45:
            ms1, ms3 = False
            ms2 = True
            self.microsteps = 4

        elif abs(deg) >= 0.225:
            ms1, ms2 = True
            ms3 = False
            self.microsteps = 8

        else:
            ms1, ms2, ms3 = False
            self.microsteps = 16

        gpio.output(self.ms1, ms1)
        gpio.output(self.ms2, ms2)
        gpio.output(self.ms3, ms3)

    def turnStep(self, deg):
        tolerance = .1125 #min number of degrees per step
        self.setStep(deg)
        if deg > tolerance:
            if cnt < ele_steps: self.move(1)
        elif deg < -tolerance:
            if cnt > 0: self.move(-1)

    def move(self, steps)
        if steps > 0:
            drc = True
            self.cnt += steps*(16 / self.microsteps)
        elif steps < 0:
            drc = False
            self.cnt -= steps*(16 / self.microsteps)
        else:
            return
        for i in range(abs(steps)):
            gpio.output(self.drc, drc)
            gpio.output(self.stp, True)
            gpio.output(self.stp, False)
            time.sleep(WaitTime)
