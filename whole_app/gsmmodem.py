import serial
import logging
import time
import queue
import threading
import os
#import smsutil
import smsforwarder


class GsmModem:
    def __init__(self, pin):
        self.logger = logging.getLogger(__name__)
        self.queue = queue.Queue()
        self.serial = serial.Serial('/dev/serial0', timeout=1)
        self.logger.info(f"Connected to GSM modem - {self.serial.name if self.serial else 'error!'}")

        self.__ignition()

        self.__execute_command('ATZ', 'setting all the parameters to defaults', ['OK', 'ERROR', '+CME ERROR'])
        time.sleep(0.3)     # from documentation: A delay of 300 ms is required before next command is sent;
                            # otherwise “OK” response may be corrupted.

        self.__execute_command('ATE0', 'disable command echo', ['OK'])

        self.__execute_command('AT+CSQ', 'checking signal quality', ['OK', '+CSQ', '+CME ERROR'])

        self.__execute_command(f'AT+CPIN={pin}', 'PIN authentication', ['OK', 'ERROR', '+CME ERROR'])

        self.__execute_command('AT+CCID', 'IMEI', ['OK', '+CCID', 'ERROR', '+CME ERROR'])

        self.__execute_command('AT+CREG?', 'network registration', ['OK', '+CREG', '+CME ERROR'])

        self.__execute_command('AT+SNFS=1', 'switching to speaker', ['OK'])

        self.__execute_command('AT+CRSL=8', 'setting ring sound level', ['OK', '+CME ERROR'])

        # 0 = PDU (default) 1 = text (mmses don't work in text mode)
        self.__execute_command('AT+CMGF=0', 'Select SMS message format (PDU mode)', ['OK'])

        # <mt> = 2 SMS-DELIVERs are routed directly to the TE using unsolicited result code: +CMT
        self.__execute_command('AT+CNMI=0,2,0,0,0', 'New SMS message indications', ['OK'])

        self.__serial_data_thread = threading.Thread(target=self.__process_serial_data)
        self.__serial_data_thread.start()

        self.__ring = 0
        self.__sms = 0

        self.__ring_thread = threading.Thread(target=self.__ring_loop)
        self.__ring_thread.start()

#    def __process_sms(self, sms):
#        print('Processing SMS')
#        sms = b'\x41\xE1\x90\x08'
#        t = smsutil.decode(sms, encoding='utf_8')
#        print(t)
#        print('End of processing SMS')

    def __process_serial_data(self):
        while True:
            while self.serial.in_waiting:
                ret = self.serial.readline()
                try:
                    ret = str(ret, encoding='utf-8').rstrip('\r\n')
                except UnicodeDecodeError as ude:
                    print(ude)
                self.logger.info(f'Received data from GSM modem:  {ret}') if ret else None
                if ret.startswith('RING'):
                    self.__ring = 1
                elif ret.startswith('ERROR'):
                    self.__ring = 0
                elif ret.startswith('CONNECT'):
                    self.__ring = 0
                elif ret.startswith('+CMT:'):
                    # next line is a message
                    ret = self.serial.readline()
                    try:
                        ret = str(ret, encoding='utf-8').rstrip('\r\n')
                    except UnicodeDecodeError as ude:
                        print(ude)
                    else:
                        self.logger.info(f'Received data from GSM modem (SMS):  {ret}')
                        # new thread is created for every sms
                        sms_forwarder_thread = threading.Thread(target=smsforwarder.forward_sms, args=(ret,))
                        sms_forwarder_thread.start()

            time.sleep(0.1)

    def __ring_loop(self):
        while True:
            if self.__ring:
                os.system('aplay ring_4s.wav')
            time.sleep(0.1)

    def __ignition(self):
        # something is wrong with my modem - it starts return something after couple of commands...
        # so this function calls AT command couple of times
        self.logger.info('Executing AT command couple of times to ignite modem')
        res_ok = False
        tries = 0

        while not res_ok:
            tries += 1
            self.serial.write(b'AT\r\n')
            time.sleep(0.1)     # short break after sending command
            while self.serial.in_waiting:
                ret = str(self.serial.readline(), encoding='utf-8').rstrip('\r\n')
                self.logger.info(f'Executing AT command - response: {ret}') if ret else None
                if ret == 'AT':
                    pass
                elif ret == 'OK':
                    res_ok = True
                elif ret:
                    self.queue.put(ret)
        self.logger.info(f'Executing AT command - done after {tries} tries')

    def __execute_command(self, command, description, expected_responses):
        self.logger.info(f"Executing {command} command - {description}")
        self.serial.write(bytes(str(command + '\r\n').encode('utf-8')))
        time.sleep(0.1)     # short break after sending command

        while self.serial.in_waiting:
            ret = str(self.serial.readline(), encoding='utf-8').rstrip('\r\n')
            self.logger.info(f"Executing {command} command - response: {ret}") if ret else None
            found = False
            if ret.startswith(command):
                found = True
            else:
                for exp_resp in expected_responses:
                    if ret.startswith(exp_resp):
                        found = True
            if not found and ret:
                self.queue.put(ret)

        self.logger.info(f"Executing command {command} - done")

    def call(self, number):
        self.serial.write(bytes(f'ATD{number}\r\n'.encode('utf-8')))
        self.logger.info(f"Calling: {number}")

    def execute_command(self, command):
        self.serial.write(bytes(f'{command}\r\n'.encode('utf-8')))
        self.logger.info(f"Executing command: {command}")
