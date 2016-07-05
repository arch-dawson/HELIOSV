# *********************************************************#
#   COSGC Presents                                                                                 #
#      __  __________    ________  _____   __    __        #
#     / / / / ____/ /   /  _/ __ \/ ___/   | |  / /        #
#    / /_/ / __/ / /    / // / / /\__ \    | | / /         #
#   / __  / /___/ /____/ // /_/ /___/ /    | |/ /          #
#  /_/ /_/_____/_____/___/\____//____/     |___/           #
#                                                          #
#                                                                                                          #
#  Copyright (c) 2016 University of Colorado Boulder       #
#  COSGC HASP Helios V Team                                                            #
# *********************************************************#

import numpy as np


class Bus:
    # Creates an I2C bus for reading from the ADCs
    # Requires 'a' or 'e' for setting the address

    def __init__(self, t, bus):
        if t is 'a':
            self.addr = 0x34
        if t is 'e':
            self.addr = 0x14
        self.main = 0b10100000 # SWAP THESE 
        self.backup = 0b10100001
        self.current = 1
        self.cmd = self.main
        self.bus = bus

    def switch(self):
        #Switch actively read pair between backup and main diode pairs
        if self.current == 0:
            self.current = 1
            cmd = self.backup
        elif self.current == 1:
            self.current = 0
            cmd = self.main
        self.bus.write(self.addr, cmd)

    def read(self):
        # Read difference from diode pair
        d = self.bus.read(self.addr, 3)
        print(self.addr, '  ', d)
        data = int.from_bytes(d, byteorder='big', signed=True)
        data = np.int32(data)
        data >>= 6
        data ^= 0x20000
        data <<= 14
        data >>= 14
        return data
