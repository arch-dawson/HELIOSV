#!/usr/bin/env python3
# RUN WITH SUDO
# CHANGE PERMISSIONS ON PORTS

import serial
import binascii
import time

class serialConn:
    def __init__(self):
        self.ser = serial.Serial()
        self.ser.baudrate = 4800
        self.ser.timeout = 1
        try:
            self.ser.port = '/dev/ttyUSB0'
            self.ser.open()
        except: # Windows compatible!  Maybe
            self.ser.port = 'COM1'
            self.ser.open()

        self.outFile = open(str(time.time())+'.txt','w+')
        return

    def __del__(self):
        str = self.ser.readline()
        while len(str) > 0:
            self.outFile.write(str.decode(encoding='latin-1',errors='replace'))
            self.outFile.write('\n')
            str = self.ser.readline()
        self.outFile.close()
        return

    def readIn(self, num):
        # Defines number of lines to read in
        for i in range(num):
            line = self.ser.readline()
            print(line)
            self.outFile.write(line.decode(encoding='latin-1',errors='replace'))
            self.outFile.write('\n')
        return

    def cmdEntry(self,cmd):
        cmdPre = b'\x01\x02'
        cmdSuf = b'\x03\x0D\x0A'
        userIn = cmd
        cmdString = """ ==== Command Entry ====
Enter a command with \\x or 0x, with a space.
Example: 0xAA 0xAA\n"""
        if not len(cmd) > 0:
            userIn = input(cmdString)
        bytes = userIn.split()
        cmd = bytearray.fromhex(bytes[0][2:]) + bytearray.fromhex(bytes[1][2:])
        # result = bytearray.fromhex('aa')
        print(cmdPre + cmd + cmdSuf)
        self.ser.write(cmdPre + cmd + cmdSuf)
        return
        
        
    def menu(self):
        done = False
        menuStr =  """==== Baby's First RealTerm ====
1. View output
2. Send a Command
3. Quit \n"""
        while not done:
            choice = input(menuStr)
            if choice == '1':
                num = input('How many lines?\n')
                self.readIn(int(num))
            elif choice == '2':
                self.cmdEntry('')
            elif choice[:2] == '0x':
                self.cmdEntry(choice)
            else:
                done = True
        return
                    
    
conn = serialConn()
conn.menu()
