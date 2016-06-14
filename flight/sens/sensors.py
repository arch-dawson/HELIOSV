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

import sched
import time
import calendar

from w1thermsensor import W1ThermSensor


PRES_ADDR = 0x28

AG_ADDR = 0x69
AG_POWER = 0x6b
AG_REG_AX = 0x3b
AG_REG_AY = 0x3d
AG_REG_AZ = 0x3f
AG_REG_GX = 0x43
AG_REG_GY = 0x45
AG_REG_GZ = 0x47

temp_cal = [58.1723, 2.0657, 2.1016, 2.1210, 1.7322, 1.4072, 2.0503, 1.9183, 1.5197, 55.7113]

class PeriodicScheduler:
    def __init__(self):
        self.scheduler = sched.scheduler(time.time, time.sleep)

    def setup(self, interval, action, actionargs=()):
        self.scheduler.enter(interval, 1, self.setup, (interval, action, actionargs))
        action(*actionargs)

    def run(self):
        self.scheduler.run()


def cs_str(data):
    out = ""
    for i in range(len(data)):
        out += "%f " % (data[i])
   # out += "%f" % (data[-1])
    return out


def capt(camera):
    t = calendar.timegm(time.gmtime())
    camera.save("/home/pi/hasp_temp/flight_anly/images/%i.png" % t)


def temp(downlink):
    try:
        data_raw = []
        data = []
        for sensor in W1ThermSensor.get_available_sensors():
            data_raw.append(sensor.get_temperature())
        for i in range(len(data_raw)):
            data.append(data_raw[i])
            #data.append(temp_cal[i] + data_raw[i])
        downlink.put(["SE", "T%i" % (len(data)), cs_str(data)])
    except:
        pass


def pres(downlink, bus):
    try:
        d = bus.read(PRES_ADDR, 2)
        data = int.from_bytes(d, byteorder='big', signed=False)
        downlink.put(["SE", "PR", " %f" % (15 * data / 0x3FFF)])
    except:
        pass


def ag_init(bus):
    bus.sm_write(AG_ADDR, AG_POWER, 0)


def ag(downlink, bus):
    try:
        time.sleep(0.05)
        data1 = bus.sm_read_word_2c(AG_ADDR, AG_REG_AX)
        data1 /= 16384.0
        data1 -= 0.0332
        time.sleep(0.05)
        data2 = bus.sm_read_word_2c(AG_ADDR, AG_REG_AY)
        data2 /= 16384.0
        data2 += 0.0635
        time.sleep(0.05)
        data3 = bus.sm_read_word_2c(AG_ADDR, AG_REG_AZ)
        data3 /= 16384.0
        data3 += 0.008
        time.sleep(0.05)
        data4 = bus.sm_read_word_2c(AG_ADDR, AG_REG_GX)
        data4 /= 131
        data4 -= 0.1608
        time.sleep(0.05)
        data5 = bus.sm_read_word_2c(AG_ADDR, AG_REG_GY)
        data5 /= 131 - 0.4527
        time.sleep(0.05)
        data6 = bus.sm_read_word_2c(AG_ADDR, AG_REG_GZ)
        data6 /= 131
        data6 -= 1.2578
        data = [data1, data2, data3, data4, data5, data6]
        downlink.put(["SE", "AG", cs_str(data)])
    except:
        pass
