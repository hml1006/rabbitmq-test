import queue
import os
import re
import psutil

def get_node_name():
    path = '/opt/midware/rabbitmq/server/etc/rabbitmq/rabbitmq-env.conf'
    if os.path.exists(path) and os.path.isfile(path):
        f = open(path, mode='r')
        while True:
            line = f.readline()
            if line == None or len(line) == 0:
                return None
            result = re.findall(r'^\s*NODENAME\=(.+)\s*$', line)
            if len(result) > 0:
                return result[0]
        return None
    return None

def get_rmq_process():
    '''
     查找rabbitmq进程
    :param keys:
    :return:
    '''
    rabbitmq = ['/opt/midware/rabbitmq/erlang/erts-10.4.4/bin/beam.smp', '/usr/lib/erlang/erts-7.3/bin/beam.smp']
    for process in psutil.process_iter():
        cmdline = process.cmdline()
        if len(cmdline) > 0:
            if cmdline[0] in rabbitmq:
                return process
    return None

def get_rmq_process_mem_usage(process):
    '''
    查找进程内存占用
    :param process:
    :return:
    '''
    if not process:
        print('process none')
        return None
    mem_info = process.memory_info()
    return mem_info.rss / 1024

def get_machine_mem_info():
    '''
    返回系统已使用内存
    :return:
    '''
    mem_info = psutil.virtual_memory()
    return ((mem_info.total - mem_info.available)/1024, mem_info.total/1024)
