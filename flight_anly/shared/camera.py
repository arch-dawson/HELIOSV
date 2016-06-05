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

import cv2
import math


class Camera:
    def __init__(self, index):
        self.cam = cv2.VideoCapture(index)
        self.index = index
        self.open()
        self.lock = threading.Lock()

    def read(self):
        try:
            with self.lock:
                ret, src = self.cam.read()
                if (src.empty()):
                    return -1
            return cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        except(KeyboardInterrupt, SystemExit):
            with self.lock:
                ret, src = self.cam.read()
                img = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
                cv2.imwrite("/home/pi/hasp_temp/flight_anly/images/keyboard_exit", img)
                self.close()
        except:
                return -1

    def save(self, file):
        img = self.read()
        return cv2.imwrite(file, img)

    def reset(self):
        self.close()
        self.open()

    def close(self):
        if self.cam.isOpened():
            self.cam.release()
        self.lock = threading.Lock()

    def open(self):
        if not self.cam.isOpened():
            self.cam.open(self.index)
