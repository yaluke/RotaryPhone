#!/usr/bin/env python3

import serial
import time

ser = serial.Serial('/dev/serial0', timeout=1)
print(ser.name)

ser.write(b'AT\r\n')
print(ser.read(128).decode('utf-8'))
time.sleep(2)

ser.write(b'ATI\r\n')
print(ser.read(256).decode('utf-8'))
time.sleep(2)

ser.write(b'AT+CSQ\r\n')
print(ser.read(128).decode('utf-8'))
time.sleep(2)

ser.write(b'AT+CPIN=1111\r\n')
print(ser.read(128).decode('utf-8'))
time.sleep(2)

ser.write(b'AT+CCID\r\n')
print(ser.read(256).decode('utf-8'))
time.sleep(2)

ser.write(b'AT+CREG?\r\n')
print(ser.read(128).decode('utf-8'))
time.sleep(2)

ser.write(b'AT+SNFS=0\r\n')
print(ser.read(128).decode('utf-8'))
time.sleep(2)

ser.write(b'AT+CRSL=2\r\n')
print(ser.read(128).decode('utf-8'))
time.sleep(2)

ser.write(b'ATD0048572292736\r\n')
print(ser.read(128).decode('utf-8'))
time.sleep(2)

