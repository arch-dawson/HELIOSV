#*********************************************************#
#   COSGC Presents					                      #
#      __  __     ___               ____ ____ ____	      #
#     / / / /__  / (_)___  _____   /  _//_  //  _/        #
#    / /_/ / _ \/ / / __ \/ ___/   / / 	 | | / /          #
#   / __  /  __/ / / /_/ (__  )  _/ /  	 | |/ /           #
#  /_/ /_/\___/_/_/\____/____/  /___/ 	 |___/	          #
#   							                          #
#  Copyright (c) 2014 University of Colorado Boulder	  #
#  COSGC HASP Helios IV Team				              #
#*********************************************************#

import threading
import logging
import queue
import numpy as np
import time
import motors_smooth
import RPi.GPIO as gpio
import diodes
import i2c

#Declare pins
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

gpio.setup(SLPA, gpio.OUT)
gpio.setup(SLPE, gpio.OUT)
gpio.output(SLPA, True)
gpio.output(SLPE, True)

#Set up instances of class
azimuth = motors_smooth.MotorAZ(STPA, DRCA, MS1A, MS2A, MS3A)
elevation = motors_smooth.MotorELE(STPE, DRCE, MS1E, MS2E, MS3E)

#Get degrees from image analysis:
'''
readingA, readingE = readings.read()
degA, degE= model.read(readingA, readingE)
'''
#Without Image Analysis, just use diode readings as degrees
i2c_bus = i2c.I2Cbus()
daz = diodes.Bus('a',i2c_bus)
delev = diodes.Bus('e',i2c_bus)
az_reading = 0
ele_reading = 0
azArray = [0]
eleArray = [0]
movingAvg = 8
a_bias = 0
e_bias = 0


try:
    while 1:
            
            time.sleep(2./6.)
            try:
                    az_reading = daz.read()
                    ele_reading = delev.read()
            except:
                    pass
            
                    
            az_deg = az_reading
            ele_deg = ele_reading
                                    
            total = 0  
            
            eleArray.append(ele_deg)			
            azArray.append(az_deg)

            azArray.pop(0)
            eleArray.pop(0)
            

            total_ele = sum(eleArray)
            total_az = sum(azArray)
            degA =  (total_az / movingAvg) + a_bias
            degE = (total_ele / movingAvg) + e_bias
            
            print("Azimuth: %f\tElevation: %f" %(degA, degE))            

            
            #Turn based on degrees
           # azimuth.turnStep(degA, False)
           # elevation.turnStep(degE, False)

except(KeyboardInterrupt, SystemExit):
	#logging.warning("Recieved keyboard interrupt, quitting threads")
	gpio.cleanup()
	exit()

