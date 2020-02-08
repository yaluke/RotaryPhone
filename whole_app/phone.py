#!/usr/bin/env python3

import rotarydial
import handset
import gsmmodem
import multiprocessing
import logging
import configparser


def config_logging():
    logging.basicConfig(filename="phone.log", style='{', format="{asctime} : {levelname:8} : {name:11} : {message}"
                        , level=logging.DEBUG)
    return logging.getLogger(__name__)


if __name__ == '__main__':
    logger = config_logging()
    logger.info("Application started")

    shortcuts = dict()
    config = configparser.ConfigParser()
    config.read('config.ini')
    email_account = ''
    email_passwd = ''
    email_to = ''
    if 'shortcuts' in config.sections():
        for opt in config.options('shortcuts'):
            shortcuts[opt] = config.get('shortcuts', opt)
        logger.info(f'{len(shortcuts)} shortcuts loaded from config.ini file')

    if 'smsforward' in config.sections():
        for opt in config.options('smsforward'):
            if opt == 'email_account':
                email_account = config.get('smsforward', opt)
            elif opt == 'email_passwd':
                email_passwd = config.get('smsforward', opt)
            elif opt == 'email_to':
                email_to = config.get('smsforward', opt)
        logger.info('Forward sms data loaded from config.ini file')

    gsm_modem = gsmmodem.GsmModem('1111', email_account, email_passwd, email_to)

    queue = multiprocessing.Queue()

    rotary_dial_thread = multiprocessing.Process(target=rotarydial.collect_number, args=(queue,))
    rotary_dial_thread.start()
    logger.info("Rotary dial process started")

    handset_thread = multiprocessing.Process(target=handset.handle_handset, args=(queue,))
    handset_thread.start()
    logger.info("Handset process started")

    while True:
        msg = queue.get()
        logger.info(f"Message received: {msg}")
        if msg[0].isnumeric():
            if len(msg) > 1:
                gsm_modem.call(msg)
            else:
                # find the shortcut and call
                number = shortcuts.get(msg)
                if number:
                    gsm_modem.call(number)
        else:
            gsm_modem.execute_command(msg)
