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
import socket
import time
import re
import subprocess

TCP_IP = '192.168.1.234'
TCP_PORT = 8080
BUFFER_SIZE = 1024

def restart():
	command = "/usr/bin/sudo /sbin/shutdown -r now"
	process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)

rebootRe=re.compile('reboot', re.IGNORECASE)

def connect():
	global s, conn, addr
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((TCP_IP, TCP_PORT))
	s.listen(1)
	conn, addr = s.accept()


def main(downlink, inputQ, nightMode):
	connect()
	nightModePrev = False

	data = conn.recv(BUFFER_SIZE).decode()
	downlink.put(["BL","RE",data])

	#downlink.put(["BL", "RE", "successful connection to upper pi"])
	while True:
		if nightMode.is_set() != nightModePrev:
			conn.send("night".encode())
			nightModePrev = nightMode.is_set()
		cmd=inputQ.get()
		if cmd == b"\x01":
			conn.send("reboot".encode())
		elif cmd == b"\x02":
			conn.send("ping".encode())
		elif cmd == b"\x03":
			conn.send("cpu".encode())
		elif cmd == b"\x04":
			conn.send("temp".encode())
		elif cmd == b"\x05":
			conn.send("disk".encode())
		elif cmd == b"\x06":
			conn.send("faster".encode())
		elif cmd == b"\x07":
			conn.send("slower".encode())
		elif cmd == b"\x08":
			conn.send("reboot".encode())
			downlink.put(["BL","BL", "     Rebooting BOTH pi's now"])
			restart()
		elif cmd == b"\x09":
			conn.send("image".encode())
		else:
			downlink.put(["BL", "ER", cmd])


		data = conn.recv(BUFFER_SIZE).decode()
		downlink.put(["BL", "RE", data])
		if rebootRe.search(data):
			s.close()
			connect()
