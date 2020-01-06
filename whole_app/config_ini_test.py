#!/usr/bin/env python3

import configparser

shs = 'shortcuts'

if __name__ == '__main__':
    shortcuts = dict()
    config = configparser.ConfigParser()
    config.read('config.ini')
    if shs in config.sections():
        for opt in config.options(shs):
            shortcuts[opt] = config.get(shs, opt)
    print(shortcuts, len(shortcuts))

    n = shortcuts.get('')
    print(n)
