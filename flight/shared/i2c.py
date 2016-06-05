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


import threading

import quick2wire.i2c
import smbus


class I2Cbus:
    def __init__(self):
        self.lock = threading.Lock()
        self.smbus = smbus.SMBus(1)

    def read(self, addr, n):
        with self.lock:
            with quick2wire.i2c.I2CMaster() as bus:
                d = bus.transaction(quick2wire.i2c.reading(addr, n))[0]
        return d

    def write(self, addr, cmd):
        with self.lock:
            with quick2wire.i2c.I2CMaster() as bus:
                bus.transaction(quick2wire.i2c.writing_bytes(addr, cmd))

    def sm_read(self, addr, reg):
        with self.lock:
            return self.smbus.read_byte_data(addr, reg)

    def sm_read_word(self, addr, reg):
        high = self.smbus.read_byte_data(addr, reg)
        low = self.smbus.read_byte_data(addr, reg + 1)
        val = (high << 8) + low
        return val

    def sm_read_word_2c(self, addr, reg):
        val = self.sm_read_word(addr, reg)
        if val >= 0x8000:
            return -((65535 - val) + 1)
        else:
            return val

    def sm_write(self, addr, reg, cmd):
        with self.lock:
            self.smbus.write_byte_data(addr, reg, cmd)
