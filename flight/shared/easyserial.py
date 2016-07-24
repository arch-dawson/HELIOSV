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

import threading

import serial


class Bus:
    def __init__(self, path, rate):
        self.bus = serial.Serial(
            port=path,
            baudrate=rate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            writeTimeout=None,
            timeout=0,
            rtscts=False,
            dsrdtr=False,
            xonxoff=False
        )
        self.lock = threading.Lock()

    def waitByte(self):
        with self.lock:
            while not self.bus.inWaiting():
                pass
            return self.bus.read()

    def inWaiting(self):
        with self.lock:
            return self.bus.inWaiting()

    def read(self, l=1):
        with self.lock:
            return self.bus.read(l)

    def write(self, data):
        with self.lock:
            self.bus.write(data.encode('utf-8'))

    def flushInput(self):
        with self.lock:
            self.bus.flushInput()
