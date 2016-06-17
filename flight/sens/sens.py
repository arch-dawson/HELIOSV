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

import sens.sensors as sensors

CAM_INTERVAL = 10  # seconds
TEMP_INTERVAL = 10
PRES_INTERVAL = 10
AG_INTERVAL = 10


def main(downlink, i2c, camera, cmd_queue, tempLED):

    sensors.ag_init(i2c)
    scheduler = sensors.PeriodicScheduler()
    scheduler.setup(AG_INTERVAL, sensors.ag, [downlink, i2c])
    scheduler.setup(CAM_INTERVAL, sensors.capt, [camera])
    scheduler.setup(TEMP_INTERVAL, sensors.temp, [downlink, tempLED])
    scheduler.setup(PRES_INTERVAL, sensors.pres, [downlink, i2c])

    scheduler.run()
    downlink.put(["SE", "BU", "SENS"])
