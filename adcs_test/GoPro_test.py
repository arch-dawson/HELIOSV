import time
import RPi.GPIO as gpio

GP_PIN = 13
gpio.setmode(gpio.BOARD)
gpio.setup(GP_PIN, gpio.OUT)
gpio.output(GP_PIN, False)

#GoPro Boot
gpio.output(GP_PIN, True)
time.sleep(2)
gpio.output(GP_PIN, False)
