#!/usr/bin/env bash
#sudo /bin/bash -c "echo 'ds1307 0x68' > /sys/class/i2c-adapter/i2c-1/new_device"

# Check for IP and Hostname
_IP=$(hostname -I) || true
_HOSTNAME=$(hostname) || true

sleep 3

# Get current RTC Time
#_TIME=$(sudo hwclock --show)
#printf "\nCurrent RTC Time: %s\n" "$_TIME"

#sleep 5

# Print system time
_TIME=$(date)
printf "Current System Time: %s\n" "$_TIME"

sleep 3

if [ "$_IP" ]; then
  # We have a network, set the hwclock from the network time!
  printf "\nCurrent IP: %s@%s\n" "$_HOSTNAME" "$_IP"

 # printf "We are connected to the internet. Setting RTC from network time\n"
  sleep 3
  sudo service ntp stop
  #sudo ntpdate time.nist.gov
  #sudo service ntp start
  #sudo hwclock --systohc -f /dev/rtc0

else
  # No network, set the time from the RTC
  printf "No network. Setting time from the RTC.\n"
  sleep 3
  sudo hwclock --hctosys -f /dev/rtc0
fi

sleep 3

_TIME=$(date)
printf "New Time: %s\n\n" "$_TIME"

# Add shift key spiffyness here

#printf "Running Upper flight loop\n"
#sudo python3 /home/pi/hasp_temp/heliosUPPER/flight_UPPER/main_UPPER.py
