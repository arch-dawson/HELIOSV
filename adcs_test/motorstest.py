import time
import RPi.GPIO as gpio
import math

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

waittime1 =(1./6.)/16
waittime2 =0

gpio.setmode(gpio.BOARD)
gpio.setup(STPA, gpio.OUT)
gpio.setup(DRCA, gpio.OUT)
gpio.setup(SLPA, gpio.OUT)
gpio.setup(STPE, gpio.OUT)
gpio.setup(DRCE, gpio.OUT)
gpio.setup(SLPE, gpio.OUT)
gpio.setup(MS1A, gpio.OUT)
gpio.setup(MS2A, gpio.OUT)
gpio.setup(MS3A, gpio.OUT)
gpio.setup(MS1E, gpio.OUT)
gpio.setup(MS2E, gpio.OUT)
gpio.setup(MS3E, gpio.OUT)



gpio.output(SLPA, True)
gpio.output(SLPE, True)


'''for i in range(0,400):
        gpio.output(DRCE, False)

        gpio.output(MS1E, True)
        gpio.output(MS2E, True)
        gpio.output(MS3E, True)

        gpio.output(STPE, True)
        gpio.output(STPE, False)
        time.sleep(waittime2)'''


microsteps = 16
cnt = 0


steps = 1600
drc = False

for i in range(steps):
    for i in range(8):
        gpio.output(DRCA, drc)
        gpio.output(MS1A, True)
        gpio.output(MS2A, True)
        gpio.output(MS3A, True)
        gpio.output(STPA, True)
        gpio.output(STPA, False)
        time.sleep(waittime1)
    time.sleep(waittime2)

gpio.cleanup()
