#!/usr/bin/env python3

"""
Simple script for testing rotary dial in old desktop phone using Raspberry Pi.
It counts impulses and measures time between them.
Rotary dial should be connected to RPi similar to tact button (how to do this properly:
https://grantwinney.com/using-pullup-and-pulldown-resistors-on-the-raspberry-pi/).

For my phone (W48mT - https://en.wikipedia.org/wiki/W48_(telephone)) rotary dial contacts are closed by default and
opened for every impulse. It produces two impulses for single dial hole (2 imp. for '1', 4 imp. for '2', ... 20 imp.
for '0'), so if one impulse is missing (it happens sometimes), proper number can be calculated.

How to check other phone:
- if rotary dial contacts are open by default -> change GPIO.FALLING to GPIO.RAISING in GPIO.add_event_detect
- play with bounce_time (set it to 1 to check how many impulses are generated, then choose something smaller that time
between impulses)

Script can be interrupted by pressing 'enter'
"""

import RPi.GPIO as GPIO
import time

rotary_dial_pin = 6
bounce_time = 30

GPIO.setmode(GPIO.BCM)
GPIO.setup(rotary_dial_pin, GPIO.IN)

counter = 0
curr_time = time.time()


def on_rotary_dial_interrupt(arg):
	global counter
	global curr_time
	new_time = time.time()
	counter += 1
	print(f'{counter}, {new_time - curr_time}')
	curr_time = new_time


GPIO.add_event_detect(rotary_dial_pin, GPIO.FALLING, callback=on_rotary_dial_interrupt, bouncetime=bounce_time)

input()

GPIO.cleanup()
