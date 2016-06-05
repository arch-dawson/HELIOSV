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


import time


def main(downlink, ground, adcs, sens, inputQ):
    downlink.put(["UP", "BU", "UPLK"])
    while True:
        time.sleep(2)
        if ground.inWaiting():
            soh = ground.read()
            stx = ground.waitByte()
            tar = ground.waitByte()
            cmd = ground.waitByte()
            etx = ground.waitByte()
            cr_ = ground.waitByte()
            lf_ = ground.waitByte()
            packet = hex(int.from_bytes((soh + stx + tar + cmd + etx), byteorder='big'))
            #downlink.put(["soh = ", hex(int.from_bytes(soh, byteorder='big')), "<3"])
            if soh == b"\x01" and etx == b"\x03":
                if stx == b"\x02":
                    if tar == b"\xAA":
                        if cmd == b"\xAA":
                            downlink.put(["UP", "AC", "ACK"])
                    elif tar == b"\xBB":
                        adcs.put(cmd)
                    elif tar == b"\xC0":
                        nudge = - int.from_bytes(cmd, byteorder='big')
                        adcs.put(nudge)
                    elif tar == b"\xC1":
                        nudge = int.from_bytes(cmd, byteorder='big')
                        adcs.put(nudge)
                    elif tar == b"\xD0":
                        nudge = - int.from_bytes(cmd, byteorder='big') - 180
                        adcs.put(nudge)
                    elif tar == b"\xD1":
                        nudge = int.from_bytes(cmd, byteorder='big') + 180
                        adcs.put(nudge)
                    elif tar == b"\xEE":
                        sens.put(cmd)
                    elif tar == b"\xFF":
                        inputQ.put(cmd)
                    else:
                        downlink.put(["UP", "ER", packet])
                elif stx == b"\x30":
                    pass  # Handle GPS data if necessary
                else:
                    downlink.put(["UP", "ER", packet])
            else:
                downlink.put(["UP", "ER", packet])
    return 0
