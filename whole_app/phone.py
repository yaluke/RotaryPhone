#!/usr/bin/env python3

import rotary_dial
import threading
import queue
import logging
import logging.handlers


def config_logging():
	logging.basicConfig(filename="phone.log", style='{', format="{asctime} : {levelname:8} : {name:11} : {message}"
						, level=logging.DEBUG)
	return logging.getLogger(__name__)

if __name__ == '__main__':
	logger = config_logging()
	logger.info("Application started")
	queue = queue.Queue()
	rotary_dial_thread = threading.Thread(target=rotary_dial.collect_number, args=(queue,))
	rotary_dial_thread.start()
	logger.info("Rotary dial thread started")
	while True:
		msg = queue.get()
		logger.info(f"Message received: {msg}")
		print(f"Received number to call: {msg}")

