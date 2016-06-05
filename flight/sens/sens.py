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
SYNC_INTERVAL = 1800
TEMP_INTERVAL = 10
PRES_INTERVAL = 10
AG_INTERVAL = 2
GP_INTERVAL = 1


def main(downlink, i2c, camera, cmd_queue):

    sensors.ag_init(i2c)
    scheduler = sensors.PeriodicScheduler()
    scheduler.setup(AG_INTERVAL, sensors.ag, [downlink, i2c])
    scheduler.setup(GP_INTERVAL, sensors.gp_check, [downlink, cmd_queue])
    scheduler.setup(CAM_INTERVAL, sensors.capt, [camera])
    scheduler.setup(TEMP_INTERVAL, sensors.temp, [downlink])
    scheduler.setup(PRES_INTERVAL, sensors.pres, [downlink, i2c])

    scheduler.run()
    downlink.put(["SE", "BU", "SENS"])
