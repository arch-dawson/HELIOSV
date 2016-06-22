#*********************************************************#
#   COSGC Presents                                                            #
#      __  __     ___               ____ ____ ____            #
#     / / / /__  / (_)___  _____   /  _//_  //  _/        #
#    / /_/ / _ \/ / / __ \/ ___/   / /   | | / /          #
#   / __  /  __/ / / /_/ (__  )  _/ /    | |/ /           #
#  /_/ /_/\___/_/_/\____/____/  /___/    |___/            #
#                                                                                 #
#  Copyright (c) 2014 University of Colorado Boulder      #
#  COSGC HASP Helios IV Team                                          #
#*********************************************************#

import threading
import logging
import queue


import time
import RPi.GPIO as gpio
from quick2wire import gpio
from quick2wire.gpio import pi_header_1, Out

WaitTime = 0.0024

class Motor():
    def __init__(self, stp, drc, ms1, ms2, ms3):
        self.stp = stp
        self.drc = drc
        self.ms1 = ms1
        self.ms2 = ms2
        self.ms3 = ms3
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
        tolerance = .1125 #min number of degrees per step (degrees per 16th step)
        #turning one step in a specified direction
        self.setStep(deg)
        if deg > tolerance:
            if cnt < ele_steps: self.move(1)

        elif deg < -tolerance:
            if cnt > 0: self.move(-1)


    def move(self, steps)
        for i in range(abs(steps)):
            if steps > 0: drc = True
            if steps < 0: drc = False
            if steps = 0: return
            gpio.output(self.drc, drc)
            gpio.output(self.stp, True)
            gpio.output(self.stp, False)
            time.sleep(WaitTime)
            self.cnt = self.cnt + (-1)*(!drc)*(16 / self.microsteps)  #add to or subtract from step count
