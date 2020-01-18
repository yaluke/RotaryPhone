#!/usr/bin/env python3

"""
    Small module responsible for killing all python processes - multiprocesses application often leave some dangling
    processes, especially during massive development.
"""

import psutil
import os
import signal
import getpass

for p in psutil.process_iter(attrs=['name', 'pid', 'username']):
    if 'python' in p.info['name'] and os.getpid() != p.info['pid'] and getpass.getuser() == p.info['username']:
        print('Killing: ', p.info['pid'], p.info['name'], p.info['username'])
        p.send_signal(signal.SIGTERM)