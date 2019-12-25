import serial
import logging
import time

class GsmModem:
    def __init__(self, pin):
        self.logger = logging.getLogger(__name__)
        self.serial = serial.Serial('/dev/serial0', timeout=1)
        self.logger.info(f"Connected to GSM modem - {self.serial.name if self.serial else 'error!'}")

        self.__ignition()

        self.serial.write(b'ATZ\r\n')
        self.logger.info(f"Setting all the parameters to defaults: {self.serial.read(256).decode('utf-8')}")
        self.serial.write(b'ATE0\r\n')
        self.logger.info(f"Disabling command echo: {self.serial.read(256).decode('utf-8')}")

        self.serial.write(b'AT+CSQ\r\n')
        self.logger.info(f"Signal quality: {self.serial.read(256).decode('utf-8')}")

        self.serial.write(bytes(f'AT+CPIN={pin}\r\n'.encode('utf-8')))
        self.logger.info(f"PIN authentication: {self.serial.read(256).decode('utf-8')}")

        self.serial.write(b'AT+CCID\r\n')
        self.logger.info(f"CCID: {self.serial.read(256).decode('utf-8')}")

        self.serial.write(b'AT+CREG?\r\n')
        self.logger.info(f"Network registration: {self.serial.read(256).decode('utf-8')}")

        self.serial.write(b'AT+SNFS=0\r\n')
        self.logger.info(f"Switching to headphones: {self.serial.read(256).decode('utf-8')}")

        self.serial.write(b'AT+CRSL=2\r\n')
        self.logger.info(f"Setting ring sound level: {self.serial.read(256).decode('utf-8')}")

    def __ignition(self):
        # something is wrong with my modem - it starts return something after couple of commands...
        # so this function asks it for manufacturer specific information couple of times
        res_lenght = 0
        tries = 0
        while res_lenght == 0:
            tries += 1
            self.serial.write(b'ATI\r\n')
            result = self.serial.read(256).decode('utf-8')
            res_lenght = len(result)
            if res_lenght > 0:
                self.logger.info(f"Manufacturer specific information (after {tries} tries): {result}")
            else:
                time.sleep(0.1)
                print(tries)


    def call(self, number):
        self.serial.write(bytes(f'ATD{number}\r\n'.encode('utf-8')))
        self.logger.info(f"Calling: {self.serial.read(256).decode('utf-8')}")


    def disconnect(self):
        self.serial.write(b'ATH\r\n')
        self.logger.info(f"Disconnecting call: {self.serial.read(256).decode('utf-8')}")
