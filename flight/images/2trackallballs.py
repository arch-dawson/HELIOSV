# import the necessary packages
from collections import deque
import numpy as np
import imutils
import io
import glob
import cv2
import os


#uncomment to use a different folder
#print "Enter the location of the files: ",
#directory = raw_input()
#path = r"%s" % directory
#for file in os.listdir(path):
#    current_file = os.path.join(path, file)
#    frame = open(current_file, "rb")


print ("opening")
with open("centers.txt", "a") as myfile:
    myfile.write("New Batch!\n")

#all files in the current folder
for filename in glob.glob("*.png"):
    frame = cv2.imread(filename)

#begin image processing code
    try:
        cv2.imshow("Image",frame)
        print("image")
        greenLower = np.array([0, 0, 0])
        greenUpper = np.array([250, 250, 250])
        
            # resize the frame, blur it, and convert it to the HSV color space
        frame = imutils.resize(frame, width=600)
        frame = imutils.resize(frame, height=480)
            # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # construct a mask for the color green, then perform
            # a series of dilations and erosions to remove any small
            # blobs left in the mask
        mask = cv2.inRange(hsv, greenLower, greenUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        mask = 255 - mask
            # find contours in the mask and initialize the current
            # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None

            # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                # only proceed if the radius meets a minimum size
            if radius > 10:
                x = x-300
                y = y-240
                print (x, y) 
                with open("centers.txt", "a") as myfile:
                    myfile.write("Pixels: %.2f, %.2f Degrees: %.2f, %.2f \n" % (x, y, x/26.2, y/27.9))
                    #myfile.write("saved")
                    print ("saving")

        key = cv2.waitKey(1) & 0xFF
    except:
        continue

# do a bit of cleanup
print("folder finished")
cv2.destroyAllWindows()
