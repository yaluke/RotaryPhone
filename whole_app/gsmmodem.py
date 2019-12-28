import serial
import logging
import time
import queue


class GsmModem:
    def __init__(self, pin):
        self.logger = logging.getLogger(__name__)
        self.queue = queue.Queue()
        self.serial = serial.Serial('/dev/serial0', timeout=1)
        self.logger.info(f"Connected to GSM modem - {self.serial.name if self.serial else 'error!'}")

        self.__ignition()

        self.__execute_ATZ_command()

        self.__execute_ATE0_command()

        self.__execute_AT_CSQ_command()

        self.__execute_AT_CPIN_command(pin)

        self.__execute_AT_CCID_command()

        self.__execute_AT_CREG_command()

        self.__execute_AT_SNFS_command()

        self.__execute_AT_CRSL_command()

        while not self.queue.empty():
            print(f'Response still in queue: {self.queue.get()}')

        # short test - it blocks main thread
        # while True:
        #    while self.serial.in_waiting:
        #        ret = str(self.serial.readline(), encoding='utf-8').rstrip('\r\n')
        #        print(ret) if ret else None
        #    time.sleep(0.1)

    def __ignition(self):
        # something is wrong with my modem - it starts return something after couple of commands...
        # so this function asks it for manufacturer specific information couple of times
        self.logger.info('Executing AT command couple of times to ignite modem')
        res_ok = False
        tries = 0

        while not res_ok:
            tries += 1
            self.serial.write(b'AT\r\n')
            time.sleep(0.1) # short break after sending command
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

    def __execute_ATZ_command(self):
        self.logger.info('Executing ATZ command - setting all the parameters to defaults')
        self.serial.write(b'ATZ\r\n')
        time.sleep(0.1)     # short break after sending command
        # expected responses: OK, ERROR/+CME ERROR
        res_ok = False
        res_error = False
        res_cme_error = False

        while self.serial.in_waiting:
            ret = str(self.serial.readline(), encoding='utf-8').rstrip('\r\n')
            self.logger.info(f'Executing ATZ command - response: {ret}') if ret else None
            if ret == 'ATZ':
                pass
            elif ret == 'OK':
                res_ok = True
            elif ret == 'ERROR':
                res_error = True
            elif ret.startswith('+CME ERROR'):
                res_cme_error = True
            elif ret:
                # non empty response not connected with this command?
                self.queue.put(ret)

        time.sleep(0.3) # from documentation: A delay of 300 ms is required before next command is sent;
                        # otherwise “OK” response may be corrupted.
        self.logger.info(f"Executting ATZ command - done, response(s): {'[OK]' if res_ok else ''} "
                         f"{'[ERROR]' if res_error else ''} {'[CME ERROR]' if res_cme_error else ''}")

    def __execute_ATE0_command(self):
        self.logger.info('Executing ATE0 command - disable command echo')
        self.serial.write(b'ATE0\r\n')
        time.sleep(0.1)     # short break after sending command
        # expected responses: OK
        res_ok = False

        while self.serial.in_waiting:
            ret = str(self.serial.readline(), encoding='utf-8').rstrip('\r\n')
            self.logger.info(f'Executin ATE0 command - response: {ret}') if ret else None
            if ret == 'ATE0':
                pass
            elif ret == 'OK':
                res_ok = True
            elif ret:
                # non empty response not connected with this command?
                self.queue.put(ret)
        self.logger.info(f"Executing ATE0 command - done, response: {'[OK]' if res_ok else ''}")

    def __execute_AT_CSQ_command(self):
        self.logger.info('Executing AT+CSQ command - checking signal quality')
        self.serial.write(b'AT+CSQ\r\n')
        time.sleep(0.1)     # short break after sending command
        # expected responses: OK, +CSQ, +CME ERROR
        res_ok = False
        res_csq = False
        res_cme_error = False

        while self.serial.in_waiting:
            ret = str(self.serial.readline(), encoding='utf-8').rstrip('\r\n')
            self.logger.info(f'Executing AT+CSQ command - response: {ret}') if ret else None
            if ret == 'AT+CSQ':
                pass
            elif ret == 'OK':
                res_ok = True
            elif ret.startswith('+CSQ:'):
                res_csq = True
            elif ret.startswith('+CME ERROR'):
                res_cme_error = True
            elif ret:
                # non empty response not connected with this command?
                self.queue.put(ret)

        self.logger.info(f"Executing AT+CSQ command - done, response(s): {'[OK]' if res_ok else ''} "
                         f"{'[CSQ]' if res_csq else ''} {'[CME ERROR]' if res_cme_error else ''}")

    def __execute_AT_CPIN_command(self, pin):
        self.logger.info('Executing AT+CPIN command - PIN authentication')
        self.serial.write(bytes(f'AT+CPIN={pin}\r\n'.encode('utf-8')))
        time.sleep(0.1)     # short break after sending command
        # expected responses: OK, ERROR, +CME ERROR
        res_ok = False
        res_error = False
        res_cme_error = False

        while self.serial.in_waiting:
            ret = str(self.serial.readline(), encoding='utf-8').rstrip('\r\n')
            self.logger.info(f'Executing AT+CPIN command - response: {ret}') if ret else None
            if ret.startswith('AT+CPIN='):
                pass
            elif ret == 'OK':
                res_ok = True
            elif ret == 'ERROR':
                res_error = True
            elif ret.startswith('+CME ERROR'):
                res_cme_error = True
            elif ret:
                # non empty response not connected with this command?
                self.queue.put(ret)

        self.logger.info(f"Executing AT+CPIN command - done, response(s): {'[OK]' if res_ok else ''} "
                         f"{'[ERROR]' if res_error else ''} {'[CME ERROR]' if res_cme_error else ''}")

    def __execute_AT_CCID_command(self):
        self.logger.info('Executing AT+CCID command - IMEI')
        self.serial.write(b'AT+CCID\r\n')
        time.sleep(0.1)     # short break after sending command
        # expected responses: OK, +CCID, ERROR, +CME ERROR (I suppose - no documentation)
        res_ok = False
        res_ccid = False
        res_error = False
        res_cme_error = False

        while self.serial.in_waiting:
            ret = str(self.serial.readline(), encoding='utf-8').rstrip('\r\n')
            self.logger.info(f'Executing AT+CCID command - response: {ret}') if ret else None
            if ret == 'AT+CCID':
                pass
            elif ret == 'OK':
                res_ok = True
            elif ret.startswith('+CCID'):
                res_ccid = True
            elif ret == 'ERROR':
                res_error = True
            elif ret.startswith('+CME ERROR'):
                res_cme_error = True
            elif ret:
                # non empty response not connected with this command?
                self.queue.put(ret)

        self.logger.info(f"Executing AT+CCID command - done, response(s): {'[OK]' if res_ok else ''} "
                         f"{'[CCID]' if res_ccid else ''} {'[ERROR]' if res_error else ''} "
                         f"{'[CME ERROR]' if res_cme_error else ''}")


    def __execute_AT_CREG_command(self):
        self.logger.info('Executing AT+CREG command - network registration')
        self.serial.write(b'AT+CREG?\r\n')
        time.sleep(0.1)     # short break after sending command
        # expected responses: OK, +CREG, +CME ERROR
        res_ok = False
        res_creg = False
        res_cme_error = False

        while self.serial.in_waiting:
            ret = str(self.serial.readline(), encoding='utf-8').rstrip('\r\n')
            self.logger.info(f'Executing AT+CREG command - response: {ret}') if ret else None
            if ret == 'AT+CREG?':
                pass
            elif ret == 'OK':
                res_ok = True
            elif ret.startswith('+CREG'):
                res_creg = True
            elif ret.startswith('+CME ERROR'):
                res_cme_error = True
            elif ret:
                # non empty response not connected with this command?
                self.queue.put(ret)

        self.logger.info(f"Executing AT+CREG command - done, response(s): {'[OK]' if res_ok else ''} "
                         f"{'[CREG]' if res_creg else ''} {'[CME ERROR]' if res_cme_error else ''}")

    def __execute_AT_SNFS_command(self):
        self.logger.info(f'Executing AT+SNFS command - switching to headphones')
        self.serial.write(b'AT+SNFS=0\r\n')
        time.sleep(0.1)     # short break after sending command
        # expected responses: OK
        res_ok = False

        while self.serial.in_waiting:
            ret = str(self.serial.readline(), encoding='utf-8').rstrip('\r\n')
            self.logger.info(f'Executing AT+SNFS command - response: {ret}') if ret else None
            if ret == 'AT+SNFS=0':
                pass
            elif ret == 'OK':
                res_ok = True
            elif ret:
                # non empty response not connected with command?
                self.queue.put(ret)

        self.logger.info(f"Executing AT+SNSF command - done, response(s): {'[OK]' if res_ok else ''}")

    def __execute_AT_CRSL_command(self):
        self.logger.info(f'Executing AT+CRSL command - setting ring sound level')
        self.serial.write(b'AT+CRSL=2\r\n')
        time.sleep(0.1)     # short break after sending command
        # expected responses: OK, +CME ERROR
        res_ok = False
        res_cme_error = False

        while self.serial.in_waiting:
            ret = str(self.serial.readline(), encoding='utf-8').rstrip('\r\n')
            self.logger.info(f'Executing AT+CRSL command - response: {ret}') if ret else None
            if ret.startswith('AT+CRSL='):
                pass
            elif ret == 'OK':
                res_ok = True
            elif ret.startswith('+CME ERROR'):
                res_cme_error = True
            elif ret:
                # non empty response not connected with this command?
                self.queue.put(ret)

        self.logger.info(f"Executing AT+CRSL command - done, response(s): {'[OK]' if res_ok else ''} "
                         f"{'[CME ERROR]' if res_cme_error else ''}")

    def call(self, number):
        self.serial.write(bytes(f'ATD{number}\r\n'.encode('utf-8')))
        self.logger.info(f"Calling: {self.serial.read(256).decode('utf-8')}")

    def disconnect(self):
        self.serial.write(b'ATH\r\n')
        self.logger.info(f"Disconnecting call: {self.serial.read(256).decode('utf-8')}")
