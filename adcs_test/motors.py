#*********************************************************#
#   COSGC Presents                                                                                #
#      __  __________    ________  _____    _____    __   #
#     / / / / ____/ /   /  _/ __ \/ ___/   /  _/ |  / /   #
#    / /_/ / __/ / /    / // / / /\__ \    / / | | / /    #
#   / __  / /___/ /____/ // /_/ /___/ /  _/ /  | |/ /     #
#  /_/ /_/_____/_____/___/\____//____/  /___/  |___/      #
#                                                         #
#                                                                                                         #
#  Copyright (c) 2015 University of Colorado Boulder      #
#  COSGC HASP Helios IV Team                                                      #
#*********************************************************#


import time
import math

import RPi.GPIO as gpio
import numpy as np


WaitTime = 0.0024
aziMaxStep = 1.8 / 4
eleMaxStep = 1.8

az_steps = 12800
ele_steps = 528

reading_tol = 1                #Noise in diode readings, needs to be calculated using diode data
m = 1                          #Relationship between diode readings and degrees off from sun, needs to be calculated
deg_tol = m*reading_tol        #Min number of degrees to turn so that payload is considered centered

gpio.setwarnings(False)
gpio.setmode(gpio.BOARD)


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
        self.microsteps = 1
        self.wait = WaitTime

    def setStep(self, deg):
        #setting microsteps based on how far away the camera is from the sun
        if abs(deg) >= 5:  # aziMaxStep:
            ms1 = False
            ms2 = False
            ms3 = False
            self.microsteps = 1

        elif abs(deg) >= 3:
            ms1 = True
            ms2 = False
            ms3 = False
            self.microsteps = 2

        elif abs(deg) >= 1.5:
            ms1 = False
            ms2 = True
            ms3 = False
            self.microsteps = 4

        elif abs(deg) >= .75:
            ms1 = True
            ms2 = True
            ms3 = False
            self.microsteps = 8

        else:
            ms1 = True
            ms2 = True
            ms3 = True
            self.microsteps = 16

        gpio.output(self.ms1, ms1)
        gpio.output(self.ms2, ms2)
        gpio.output(self.ms3, ms3)

    def turnStep(self, deg, blocking):
        deg_tol = 0.5  # min degrees per step (verify with gear ratio)
        self.setStep(deg)
        if blocking:
            steps = deg / (aziMaxStep / self.microsteps)
            self.wait = 1. / 12.

            #case in which a nudge would send it over 360 degrees
            if self.cnt + steps > az_steps:
                self.move(-self.cnt)
                steps += self.cnt - az_steps
        else:
            steps = np.sign(deg)
        if abs(deg) > deg_tol:
            if abs(self.cnt) < az_steps:
                self.move(steps)
            else:
                self.setStep(aziMaxStep)
                self.move(-self.cnt)

    def move(self, steps):
        steps = math.floor(steps)
        if steps > 0:
            drc = True
            self.cnt += steps * (16 / self.microsteps)
        elif steps < 0:
            drc = False
            self.cnt += steps * (16 / self.microsteps)
        else:
            return
        for i in range(abs(steps)):
            gpio.output(self.drc, drc)
            gpio.output(self.stp, True)
            gpio.output(self.stp, False)
            time.sleep(self.wait)


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
        self.microsteps = 1
        self.wait = WaitTime

    def setStep(self, deg):
        #setting microsteps based on how far away the camera is from the sun
        if abs(deg) >= 5:
            ms1 = False
            ms2 = False
            ms3 = False
            self.microsteps = 1

        elif abs(deg) >= 3:
            ms1 = True
            ms2 = False
            ms3 = False
            self.microsteps = 2

        elif abs(deg) >= 1.5:
            ms1 = False
            ms2 = True
            ms3 = False
            self.microsteps = 4

        elif abs(deg) >= 0.75:
            ms1 = True
            ms2 = True
            ms3 = False
            self.microsteps = 8

        else:
            ms1 = True
            ms2 = True
            ms3 = True
            self.microsteps = 16

        gpio.output(self.ms1, ms1)
        gpio.output(self.ms2, ms2)
        gpio.output(self.ms3, ms3)

    def turnStep(self, deg, blocking):
        self.setStep(deg)
        if blocking:
            steps = deg / (eleMaxStep / self.microsteps)
            self.wait = 1./12.
            #If nudging would put elevation too high or low
            if steps + self.cnt > ele_steps:
                steps = ele_steps - self.cnt
            elif steps + self.cnt < 0:
                steps = -self.cnt
        else:
            steps = np.sign(deg)
        if abs(deg) > deg_tol:
            if self.cnt >= 0:
                if self.cnt < ele_steps:
                    self.move(steps)
                else:
                    if steps > 0:
                        self.move(steps)
            else:
                if steps < 0:
                    self.move(steps)

    def move(self, steps):
        steps = math.floor(steps)
        if steps < 0:
            drc = False
            self.cnt += -steps * (16 / self.microsteps)
        elif steps > 0:
            drc = True
            self.cnt += -steps * (16 / self.microsteps)
        else:
            return
        for i in range(abs(steps)):
            gpio.output(self.drc, drc)
            gpio.output(self.stp, True)
            gpio.output(self.stp, False)
            time.sleep(self.wait)
