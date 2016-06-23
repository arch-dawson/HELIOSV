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
import logging
import queue
import cv2
import numpy as np

# Field of view of analysis camera
x_fov = 22.9
y_fov = 17.2


class calibrate:
    """
    Analysis script for image analysis
    """

    def __init__(self, cam):
        """
        Initialize

        :param model:      Model of diode reading differences
        :param ele_diodes: Elevation diodes object
        :param azi_diodes: Azimuth diodes object
        :param cam:        Camera object
        :param downlink:   Downlink thread for data transmit
        :return:           None
        """
        # Initialize self variables
        self.cam = cam

    def capture(self):
        """
        Capture picture from cam object

        :return: Received Image
        """
        return self.cam.read()

    def analyze(self):
        """
        Perform Hough Circle analysis to find the Sun
        Update diode readings, take image, analyze, update model if the Sun is found
        If no Sun is found, try finding the brightest spot

        :param: v: Verbose
        :return:   None
        """
        img = self.capture()
        if (img == -1): # Added because of weird cv2 error
            print("Unsuccessful image capture, see cali.analyze")
            return 0,0,0
        ret, img = cv2.threshold(img, 250, 255, cv2.THRESH_BINARY)
        img = cv2.blur(img, (5, 5))
        height, width = img.shape
        centerPt = (width / 2, height / 2)
        pixelDegX = width / x_fov
        pixelDegY = height / y_fov

        circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 50,
                                   param1=50, param2=23, minRadius=0,
                                   maxRadius=0)

        # try:
        if circles is not None: # If the sun is in the FOV
            circles = circles[0, :].astype(int)
            if len(circles) == 1:
                x, y, r = circles[0] # Find the x and y position of the sun and its radius
                ret = 1
                aziDegDiff = (centerPt[0] - x) / pixelDegX # How far off in azimuth are we
                eleDegDiff = (centerPt[1] - y) / pixelDegY # How far off in elevation are we
            else: # If there is more than one circle of light in the FOV
                ret = len(circles)
                aziDegDiff = 0
                eleDegDiff = 0
        else: # If the sun is not in the FOV
            print("Image taken, no Suns")
            ret = 0
            aziDegDiff = 0
            eleDegDiff = 0

        return ret, aziDegDiff, eleDegDiff
        # ret is the number of circles of light found in the image
