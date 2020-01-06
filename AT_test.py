#!/usr/bin/env python3

import serial
import time

ser = serial.Serial('/dev/serial0', timeout=1)
print(ser.name)

while True:
	cmd = input("Command: ")
	cmd += '\r\n'
	ret_size = 0
	while ret_size == 0:
		ser.write(cmd.encode('utf-8'))
		print("="*40)
		ret = ser.read(256).decode('utf-8')
		ret_size = len(ret)
		print(len(ret))
		print(type(ret))
		print(ret)
		print("="*40)
