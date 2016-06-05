import numpy as np
import cv2
import time
import calendar
import math

# Capture video from camera
ADCS_cam = cv2.VideoCapture(1)
if not ADCS_cam.isOpened():
    ADCS_cam.open(1)

t = 1

while(ADCS_cam.isOpened()):

    # Capture frame-by-frame
    ret, frame = ADCS_cam.read()

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # File save location
    file = "/home/pi/hasp_temp/adcs_test/camera_test_images/%i.png" %t

    # Adding crosshairs to the image
    img = gray
    height, width = img.shape
    height = int(height)
    width = int(width)
    x1a = math.floor(-width - 100)
    x1b = math.floor(width + 100)
    y1 = math.floor(height/2)
    pt1 = (int(x1a), int(y1))
    pt2 = (int(x1b), int(y1))
    x2 = math.floor(width/2)
    y2a = math.floor(height + 100)
    y2b = math.floor(-height - 100)
    pt3 = (int(x2), int(y2a))
    pt4 = (int(x2), int(y2b))
    cv2.line(img, pt1, pt2, (0,255,0),1)
    cv2.line(img, pt3, pt4, (0,255,0),1)
    
    # Save the image
    cv2.imwrite(file,img)

    # Display the resulting frame
    cv2.imshow('frame',img)
    t = t+1 
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
ADCS_cam.release()

cv2.destroyAllWindows()
