# import the necessary packages
from __future__ import print_function
from imutils.video import VideoStream
from collections import deque
import numpy as np
import datetime
import argparse
import imutils
import time
import cv2
import sys
sys.path.append('/usr/local/lib/pythong2.7/site-packages')
#from picamera.array import PiRGBArray
#from picamera import PiCamera
#import picamera

# initialize the video streams and allow them to warmup
print("[INFO] starting cameras...")

#picam
#camera = picamera.PiCamera()
#camera.resolution = (640, 480)
#camera.framerate = 32


#ap = argparse.ArgumentParser()
#args = vars(ap.parse_args())
#ap.add_argument("-v", "--video",
#    help="path to the (optional) video file")
#camera = cv2.VideoCapture(args["video"])



#usbcam
camera = cv2.VideoCapture(0)

#camera = VideoStream(usePiCamera=True).start()
time.sleep(2.0)


greenLower = np.array([0, 0, 0])
greenUpper = np.array([250, 250, 250])

pts = deque(maxlen=16)

ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=32,
    help="max buffer size")
args = vars(ap.parse_args())
while True:
    # grab the current frame
    (grabbed, frame) = camera.read()

    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if args.get("video") and not grabbed:
        break

    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width=600)
    frame = imutils.resize(frame, height=480)
    # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "green", then perform
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
    # it to compute the minimum enclosing circle and
    # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        # only proceed if the radius meets a minimum size
        if radius > 10:
            print ((x-300, y-240))
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),
            (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            cv2.line(frame, (300,0),(300,480), (255,0,0), 2)
            cv2.line(frame, (0,240),(600,240), (255,0,0), 2)

    # update the points queue
    pts.appendleft(center)
    # loop over the set of tracked points
    for i in xrange(1, len(pts)):
    # if either of the tracked points are None, ignore
    # them
        if pts[i - 1] is None or pts[i] is None:
            continue

        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i- 1], pts[i], (0, 0, 255), thickness)

    # show the frame to our screen
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()


# do a bit of cleanup
print("[INFO] cleaning up...")
cv2.destroyAllWindows()
camera.stop()
