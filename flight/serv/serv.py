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
import threading

class Connection():
	def __init__(self, downlink, inputQ, nightMode):
		# Set up external arguments
		self.downlink = downlink
		self.inputQ = inputQ
		self.nightMode = nightMode
		self.TCP_IP = '192.168.1.234' # 127.0.0.1 works too, may need to change clnt
		self.TCP_PORT = 8080
		self.BUFFER_SIZE = 1024

		# Successful bootup
		self.downlink.put(["SV", "BU", "SERV"])

		# Night mode default is false
		self.nightModePrev = False

		# Create server connection
		self.connect()

		# Run flight loop
		self.flight()

	def checkNight(self): # Check if night mode has changed
		if self.nightMode.is_set() != self.nightModePrev:
			self.nightModePrev = self.nightMode.is_set()
			return True
		else:
			return False

	def heartBeat(self, message):
		if checkNight():
			message.append(' night')
		#self.conn.send(message.encode())
		print(message)

	def connect(self):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.s.bind((self.TCP_IP, self.TCP_PORT))
		self.s.listen(5)
		self.conn, self.addr = self.s.accept()

	def receive(self):
		self.data = self.conn.recv(self.BUFFER_SIZE).decode()
		if self.data != None:
			self.downlink.put(["BL", "HB", self.data]) 

	def restart(self):
		command = "/usr/bin/sudo /sbin/shutdown -r now"
		process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
		self.s.close()

	def command(self):
		message = "heartbeat"
		cmd = inputQ.get()
		if cmd == b"\x01":
			message.append(" reboot")
		elif cmd == b"\x02":
			message.append(" ping")
		elif cmd == b"\x03":
			message.append(" cpu")
		elif cmd == b"\x04":
			message.append(" temp")
		elif cmd == b"\x05":
			message.append(" disk")
		elif cmd == b"\x06":
			message.append(" faster")
		elif cmd == b"\x07":
			message.append(" slower")
		elif cmd == b"\x08":
			message.append(" reboot")
			threading.Timer(5.0, self.restart).start()
		elif cmd == b"\x09":
			message.append(" image")
		elif len(cmd) > 0:
			self.downlink.put(["SV", "BL", "ER"])
		return message			

	def flight(self):
		self.downlink.put(["BL","BU","CLNT"])
		while True:
			print(self.inputQ.empty())
			if not self.inputQ.empty():
				message = self.command()
			else: 
				message = "heartbeat"
			self.heartBeat(message)
			time.sleep(3)
			self.receive()
			time.sleep(2)


def main(downlink, inputQ, nightMode):
	connection = Connection(downlink, inputQ, nightMode)
