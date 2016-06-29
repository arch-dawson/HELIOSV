# *********************************************************#
#   COSGC Presents                                         #
#      __  __________    ________  _____   __    __        #
#     / / / / ____/ /   /  _/ __ \/ ___/   | |  / /        #
#    / /_/ / __/ / /    / // / / /\__ \    | | / /         #
#   / __  / /___/ /____/ // /_/ /___/ /    | |/ /          #
#  /_/ /_/_____/_____/___/\____//____/     |___/           #
#                                                          #
#                                                          #
#  Copyright (c) 2016 University of Colorado Boulder       #
#  COSGC HASP Helios V Team                                #
# *********************************************************#
import time
from zlib import adler32

# Write data to sender-specific data log file on board flight
def logdata(packet, sender):
    if sender == "AD":
        with open("/home/pi/HELIOSV/flight/adcs.log", 'a') as log:
            log.write(packet)
        print(packet, end="")

    if sender == "UP":
        with open("/home/pi/HELIOSV/flight/uplk.log", 'a') as log:
            log.write(packet)
        print(packet, end="")

    if sender == "SE":
        with open("/home/pi/HELIOSV/flight/sens.log", 'a') as log:
            log.write(packet)
        print(packet, end="")

    if sender == "DW":
        with open("/home/pi/HELIOSV/flight/dwlk.log", 'a') as log:
            log.write(packet)
        print(packet, end="")
    if sender == "SV": # Server
        with open("/home/pi/HELIOSV/flight/serv.log", 'a') as log:
            log.write(packet)
        print(packet, end="")


def main(downlink, gnd):
    downlink.put(["DW", "BU", "DWNL"])
    while True:
        # All downlinked data must be in this form:
        # [2 char sender, 2 char record type, string of data]
        # Multi-item data needs to be in the form of ###, ###, ###
        packet = downlink.get()
        sender, record, data = packet[0], packet[1], packet[2]
        l = len(data)
        if type(data) is not bytes:
            a_data = data.encode('utf-8')
        else:
            a_data = data
        ck = adler32(a_data) & 0xffffffff
        t = time.time()  # Sec from epoch
        packet = "\x01CU HE %s %s %.2f %i %i\x02" % (sender, record, t, l, ck) + " " + data + "\x03\n"
        with open("/home/pi/HELIOSV/flight/downlink.log", 'a') as log:
            log.write(packet)
        gnd.write(packet)
        logdata(packet, sender)

    return 0
