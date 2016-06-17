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

msgLock = threading.Lock()
# Make sure message can only be changed by one thing at a time 

class Connection():
	def __init__(self, downlink, inputQ, nightMode):
		# Set up external arguments
		self.downlink = downlink
		self.inputQ = inputQ
		self.nightMode = nightMode
		self.TCP_IP = '127.0.0.1' # 127.0.0.1  or 192.168.1.234
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
		with msgLock:
			if checkNight():
				self.message.append(' night')
			self.conn.send(message.encode())
			print(self.message)
			self.message = "heartbeat"
		threading.Timer(5.0, self.heartBeat).start()

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
		cmd = inputQ.get()
		with msgLock:
                        if cmd == b"\x01":
                                self.message.append(" reboot")
                        elif cmd == b"\x02":
                                self.message.append(" ping")
                        elif cmd == b"\x03":
                                self.message.append(" cpu")
                        elif cmd == b"\x04":
                                self.message.append(" temp")
                        elif cmd == b"\x05":
                                self.message.append(" disk")
                        elif cmd == b"\x06":
                                self.message.append(" faster")
                        elif cmd == b"\x07":
                                self.message.append(" slower")
                        elif cmd == b"\x08":
                                self.message.append(" reboot")
                                threading.Timer(7.0, self.restart).start()
                        elif cmd == b"\x09":
                                self.message.append(" image")
                        elif len(cmd) > 0:
                                self.downlink.put(["SV", "BL", "ER"])			

	def flight(self):
		self.downlink.put(["BL","BU","CLNT"])
		threading.Timer(5.0, self.heartBeat).start()
		while True:
			print(self.inputQ.empty())
			if not self.inputQ.empty():
				self.command()
			self.receive()

def main(downlink, inputQ, nightMode):
	connection = Connection(downlink, inputQ, nightMode)
