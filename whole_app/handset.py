#!/usr/bin/env python3

"""
Module responsible for handset
"""

import RPi.GPIO as GPIO
import multiprocessing
import logging

handset_pin = 12
bounce_time = 50

def handle_handset(queue):
    logger = logging.getLogger(__name__)
    logger.info('Starting handset loop')

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(handset_pin, GPIO.IN)

    if GPIO.input(handset_pin):
        logger.info('Handset picked up')
    else:
        logger.info('Handset hanged up')
    while True:
        try:
            channel = GPIO.wait_for_edge(handset_pin, GPIO.BOTH, bouncetime=bounce_time)
            if channel:
                if GPIO.input(handset_pin):
                    logger.info('Handset picked up')
                    queue.put('ATA')
                else:
                    logger.info('Handset hanged up')
                    queue.put('ATH')
        except KeyboardInterrupt as ki:
            print(ki)


if __name__ == '__main__':
    logging.basicConfig(filename="handset.log", style='{', format="{asctime} : {levelname:8} : {name:11} : {message}"
                        , level=logging.DEBUG)
    queue = multiprocessing.Queue()
    handle_handset(queue)
