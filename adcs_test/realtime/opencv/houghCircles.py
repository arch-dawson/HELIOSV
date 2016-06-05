import numpy as np
import cv2
import sys

# Read in file
gimg = cv2.imread('/home/pi/hasp_temp/adcs_test/ProcessingImages/found_0.png')

# Get dimensions
height, width, depth = gimg.shape
print ('Dims', height, width)

pixelDegreeX = width / 22.9 # pixels/degree
pixelDegreeY = height / 17.2
#Can be removed in future if monochromatic
gimg = cv2.cvtColor(gimg, cv2.COLOR_BGR2GRAY)

# Find those circles!
circles = cv2.HoughCircles(gimg, cv2.HOUGH_GRADIENT, 1, 10,
                           param1=50,param2=25,minRadius=0,maxRadius=0)

try:
	a, b, c = circles.shape
except:
	print ('No circles found!!!')
	sys.exit()

print('circles.shape')
print(a,b,c)
print('Found %d circles!' % b)

''' Filter out circles that don't meet constraint '''

# Convert back to BGR so the markings are in color
gimg = cv2.cvtColor(gimg, cv2.COLOR_GRAY2BGR)

# Define important points
p11 = (int(width/2), 0)
p12 = (int(width/2), height)

p21 = (0, int(height/2))
p22 = (width, int(height/2))

# Center point and center lines
centerPt = (width/2, height/2)
cv2.line(gimg, p11,p12, (0,0,255), 1)
cv2.line(gimg, p21,p22, (0,0,255), 1)

# Get dimensions of number of found circles
rows, cols = circles[0,:].shape

# Draw the found circles
for i in range(b):
  cv2.circle(gimg, (circles[0][i][0], circles[0][i][1]), circles[0][i][2], (0, 255, 0), 2)
  cv2.circle(gimg, (circles[0][i][0], circles[0][i][1]), 2, (255,0,0), 3, cv2.LINE_AA)


print('CenterPtY: ', circles[0][0][1])
print('CenterPtX: ', circles[0][0][0])

deltaY = centerPt[1] - circles[0][0][1] # pixels
deltaX = centerPt[0] - circles[0][0][0]

print('XDist off, YDist off', deltaX, deltaY)

calDegY = deltaY / pixelDegreeY # degrees
calDegX = deltaX / pixelDegreeX
print('CalDegX: %f \t CalDegY: %f' % (calDegX, calDegY))

cv2.imshow("detected circles", gimg)
cv2.waitKey(0)

cv2.imwrite("testCal2.png", gimg)
