#*********************************************************#
#   COSGC Presents                                                                                #
#      __  __     ___               ____________                  #
#     / / / /__  / (_)___  _____   /  _/  _/  _/                  #
#    / /_/ / _ \/ / / __ \/ ___/   / / / / / /                    #
#   / __  /  __/ / / /_/ (__  )  _/ /_/ /_/ /                     #
#  /_/ /_/\___/_/_/\____/____/  /___/___/___/                     #
#                                                                                                         #
#  Copyright (c) 2014 University of Colorado Boulder      #
#  COSGC HASP Helios III Team                                                     #
#*********************************************************#

#import numpy as np
from PIL import Image, ImageFilter

def analyze(image):
    imb = image.convert(mode="1")
    imb.show()
    ime = imb.filter(ImageFilter.FIND_EDGES)
    ime.show()
    return ime

test = Image.open("sun2.png")
test.show()
analyze(test)
