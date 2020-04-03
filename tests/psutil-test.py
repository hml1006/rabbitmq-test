#!/usr/bin/python3

import psutil

def find_rabbitmq_pid():
    '''
    查找rabbitmq服务器pid
    '''
    for process in psutil.process_iter():
        cmdline = process.cmdline()
        cmdline = ''.join(cmdline)
        if cmdline.find('beam.smp') != -1 and cmdline.find('rabbitmq') != -1:
            return process.pid

print(find_rabbitmq_pid())