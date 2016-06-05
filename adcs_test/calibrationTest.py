ximport cv2
import numpy as np
import time
import diodes
import RPi.GPIO as gpio

#set up GPIO pins
STPA = 37
DRCA = 16
SLPA = 35
STPE = 38
DRCE = 40
SLPE = 36
MS1A = 29
MS2A = 31
MS3A = 33
MS1E = 15
MS2E = 32
MS3E = 11

gpio.setmode(gpio.BOARD)
gpio.setup(STPA, gpio.OUT)
gpio.setup(DRCA, gpio.OUT)
gpio.setup(SLPA, gpio.OUT)
gpio.setup(MS1A, gpio.OUT)
gpio.setup(MS2A, gpio.OUT)
gpio.setup(MS3A, gpio.OUT)

gpio.setup(STPE, gpio.OUT)
gpio.setup(DRCE, gpio.OUT)
gpio.setup(SLPE, gpio.OUT)
gpio.setup(MS1E, gpio.OUT)
gpio.setup(MS2E, gpio.OUT)
gpio.setup(MS3E, gpio.OUT)

gpio.output(SLPA, True)
gpio.output(SLPE, True)

gpio.output(MS1A, False)
gpio.output(MS2A, False)
gpio.output(MS3A, False)

gpio.output(MS1E, False)
gpio.output(MS2E, False)
gpio.output(MS3E, False)

WAITTIME = 1./6.
az_reading = 0
ele_reading = 0

azArray = [0]
azCaliArray = [0]
eleArray = [0]
eleCaliArray = [0]
movingAvg = 8
a_bias = -2
e_bias = 3
az_tolerance = 1
ele_tolerance  =  3
daz = diodes.Bus('t')
delev = diodes.Bus('p')

outfile = open("/home/pi/hasp_temp/adcs_test/ProcessingImages/outputfile.txt", "a")

'''
Get diode readings and move structure
Capture image and compare to get how off from actual the diodes are
Move the structure by how off they are, and store the info for a correlation
'''

# Initiate and connect
cap = cv2.VideoCapture(0)
if cap.isOpened():
	print("Camera open...")
else:
	cap.open()
	print("Camera opened...")

k = 0
j = 0

while 1:
    '''
    try:
        az_reading = daz.read()
        ele_reading = delev.read()
    except:
        pass

    az_deg = az_reading
    ele_deg = ele_reading

    total = 0

    eleArray.append(ele_deg)
    azArray.append(az_deg)

    azArray.pop(0)
    eleArray.pop(0)

    total_ele = sum(eleArray)
    total_az = sum(azArray)
    az_deg = (total_az / movingAvg) + a_bias
    ele_deg = (total_ele / movingAvg) + e_bias

    print('Azimuth: %f\tElevation: %f' % (az_deg, ele_deg))

    if ((az_deg) > az_tolerance):
        gpio.output(DRCA, True)

        gpio.output(STPA, True)
        gpio.output(STPA, False)
        time.sleep(WAITTIME)
    elif ((az_deg) < (-1*az_tolerance)):
        gpio.output(DRCA, False)

        gpio.output(STPA, True)
        gpio.output(STPA, False)
        time.sleep(WAITTIME)
    else:
        pass

    if ((ele_deg) > ele_tolerance):
        gpio.output(DRCE, False)

        gpio.output(STPE, True)
        gpio.output(STPE, False)
        time.sleep(WAITTIME)
    elif((ele_deg) < (-1*ele_tolerance)):
        gpio.output(DRCE, True)

        gpio.output(STPE, True)
        gpio.output(STPE, False)
        time.sleep(WAITTIME)
    else:
        pass
    '''

    # Capture Image
    ret, src = cap.read()
    gimg = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

    # Image filtering
    ret, gimg = cv2.threshold(gimg, 250, 255, cv2.THRESH_BINARY)
    gimg = cv2.blur(gimg, (5,5))
    height, width = gimg.shape

    # sun == 1/2 degree diameter
    # fov of camera = 22.9 x 17.2 degree
    # Only off by about 0.01, but might as well
    pixelDegreeX = width / 22.9 # pixels/degree
    pixelDegreeY = height / 17.2

    # Find circles
    circles = cv2.HoughCircles(gimg, cv2.HOUGH_GRADIENT, 1, 50,
                               param1=50,param2=23,minRadius=0,maxRadius=0)
    '''
    Sort circles based on diameter
    '''

    try:
        print(circles)
        a, b, c = circles.shape
        print('Found %d circles!' % b)
        cv2.imwrite('ProcessingImages/found_%d.png'%j, gimg)
        j=j+1
    except:
        print('No circles found!!!')
        cv2.imwrite('ProcessingImages/notFound_%d.png'%k, gimg)
        k=k+1
        continue

    # Calibration calcs
    centerPt = (width/2, height/2)
    deltaY = centerPt[1] - circles[0][0][1] # pixels
    deltaX = centerPt[0] - circles[0][0][0]

    calDegY = (deltaY / pixelDegreeY)*10 # degrees
    calDegX = (deltaX / pixelDegreeX)*10

    # Might be unnecessary depending on how calibration data is stored
    eleCaliArray.append(calDegY)
    azCaliArray.append(calDegX)

    print('Azimuth Off: %f\tElevation Off: %f' % (calDegX, calDegY))
    outfile.write('found_%d\tAzimuth Off: %f\tElevation Off: %f\n' %
				   (j,calDegX, calDegY))

    if(calDegX > az_tolerance):
        gpio.output(DRCA, True)

        gpio.output(STPA, True)
        gpio.output(STPA, False)
        time.sleep(WAITTIME)
    if(calDegX < (-1*az_tolerance)):
        gpio.output(DRCA, False)

        gpio.output(STPA, True)
        gpio.output(STPA, False)
        time.sleep(WAITTIME)
    else:
        pass

    if(calDegY > ele_tolerance):
        gpio.output(DRCE, True)

        gpio.output(STPE, True)
        gpio.output(STPE, False)
        time.sleep(WAITTIME)
    elif(calDegY < (-1*ele_tolerance)):
        gpio.output(DRCE, True)

        gpio.output(STPE, True)
        gpio.output(STPE, False)
        time.sleep(WAITTIME)
    else:
        pass

    '''
    Send calibration data
    '''
    print('Waiting...')
    time.sleep(WAITTIME)
    circles=0

cap.release()
gpio.cleanup()
