import diodes
import time
import i2c

i2c_bus = i2c.I2Cbus()
azimuth = diodes.Bus('a',i2c_bus)
elevation = diodes.Bus('e',i2c_bus)

while 1:
    time.sleep(1./6.)
    a_reading = azimuth.read()
    e_reading = elevation.read()
    print("Azimuth: %f       Elevation: %f " %(a_reading,e_reading))
