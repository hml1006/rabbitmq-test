import argparse
import sys
import os
import re
import subprocess
import time
import datetime
import json
import requests
import base64
import config.config as rmqcfg
import config.task as rmqtask
from exec.command import Command

# 全局日志配置
LOG_SERVER_URL = None

# 添加测试任务, POST
TASK_ADD_URL = '/tasks'
# 添加统计条目, POST
TASK_STAT_ADD = '/tasks/{id}/stats'

# 全局key设置, 针对需要执行多个任务的测试, 如果任务名称和key相同, 则测试结果认为属于同一个测试任务
TASK_KEY = int(time.mktime(datetime.datetime.now().timetuple()))

# 需要分析的日志格式
# id: queuetest2, time: 2.000s, sent: 1001 msg/s, received: 501 msg/s, min/median/75th/95th/99th consumer latency: 447660/696961/821878/921988/941319 µs
# id: test-134948-252, time: 1.477s, sent: 131940 msg/s
# id: test-134939-786, time: 11.555s, received: 41666 msg/s, min/median/75th/95th/99th consumer latency: 1637/2060/2270/2386/2407 ms
#
# 预先编译正则表达式, 提取任务id和时间
RE_TASK_INFO = re.compile(r'id:\s*(.*),\s*time:\s([0-9\.]+)s')
# 提取消息发送数量
RE_SENT = re.compile(r'sent:\s*(\d+)\s*msg/s')
# 提取消息接收数量
RE_RECEIVED = re.compile(r'received:\s*(\d+)\s*msg/s')
# 提取消息延迟
RE_LATENCY = re.compile(r'latency:\s*(\d+)/(\d+)/(\d+)/(\d+)/(\d+)\s*(µs|ms|s|ns)')

def print_help_and_exit(parser):
    '''
    打印帮助信息并退出程序
    :param parser:
    :return:
    '''
    parser.print_help()
    sys.exit(-1)

# http session
session = None
def send_http_req(url, json_str):
    '''
    把数据发送到日志收集服务器
    :param url:
    :param json_str:
    :return: 返回http状态吗和数据
    '''
    global session
    if not session:
        session = requests.Session()
    ret = session.post(url, data=json_str)
    return (ret.status_code, ret.json())

def send_log(line, url):
    '''
    把行日志提取有效数据并发送到日志服务器
    :param line:
    :return:
    '''
    if not line or len(line) == 0:
        print('line empty')
        return
    task_info = re.findall(RE_TASK_INFO, line)
    if len(task_info) == 0:
        print('task info not found')
        return
    log_info = dict()
    log_info['task_id'] = task_info[0][0]
    # 日志时间设置未当前unix时间戳
    log_info['time'] = int(time.mktime(datetime.datetime.now().timetuple()))

    # 获取发送消息速率
    sent = re.findall(RE_SENT, line)
    if len(sent) > 0:
        log_info['sent'] = int(sent[0])

    # 获取接收消息速率
    received = re.findall(RE_RECEIVED, line)
    if len(received) > 0:
        log_info['received'] = int(received[0])

    # 获取延迟数据
    latency = re.findall(RE_LATENCY, line)
    if len(latency) > 0:
        latency_dict = dict()
        # 获取时间单位
        unit = latency[0][5]
        latency_dict['min'] = int(latency[0][0])
        latency_dict['median'] = int(latency[0][1])
        latency_dict['75th'] = int(latency[0][2])
        latency_dict['95th'] = int(latency[0][3])
        latency_dict['99th'] = int(latency[0][4])
        # 单位换算, 统一用ms
        if 'µs' == unit:
            latency_dict['min'] = latency_dict['min'] / 1000
            latency_dict['median'] = latency_dict['median'] / 1000
            latency_dict['75th'] = latency_dict['75th'] / 1000
            latency_dict['95th'] = latency_dict['95th'] / 1000
            latency_dict['99th'] = latency_dict['99th'] / 1000
        elif 's' == unit:
            latency_dict['min'] = latency_dict['min'] * 1000
            latency_dict['median'] = latency_dict['median'] * 1000
            latency_dict['75th'] = latency_dict['75th'] * 1000
            latency_dict['95th'] = latency_dict['95th'] * 1000
            latency_dict['99th'] = latency_dict['99th'] * 1000
        log_info['latency'] = latency_dict
    json_str = json.dumps(log_info)
    print(json_str)
    send_http_req(json_str, url)

def execute_command(command: Command):
    '''
    执行测试命令
    :param command:
    :return:
    '''
    # 准备执行命令之前,先向日志采集服务器添加任务
    task_name = command.task.name
    task_type = command.type
    start_time = int(time.mktime(datetime.datetime.now().timetuple()))
    params = base64.b16encode(json.dumps(command.task.config).encode(encoding='utf8'))
    task_obj = {
        'name': task_name,
        'start_time': start_time,
        'type': task_type,
        'key': TASK_KEY,
        'params': params.decode(encoding='utf8')
    }
    task_url = LOG_SERVER_URL + TASK_ADD_URL
    (status_code, ret) = send_http_req(task_url, json_str=json.dumps(task_obj))
    if status_code == 200:
        print('add task %s success' % task_name)
        # 获取任务在数据库中的id
        if ret['errcode'] == 0:
            task_id = ret['task_id']
        else:
            print('add task %s failed: %s' % (task_name, ret['errstr']))
            return
    else:
        print('add task %s failed' % task_name)
        return

    # 组装添加统计信息url
    log_url = LOG_SERVER_URL + TASK_STAT_ADD.replace('{id}', str(task_id))

    # 构造命令
    command_line = command.build_command()
    print('command: %s' % command_line)
    # 执行命令
    process = subprocess.Popen(command_line, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, close_fds=True)
    if not process:
        raise Exception('cannot execute command')
    while True:
        # 按行读取测试工具输出
        data = process.stdout.readline()
        if data and len(data) > 0:
            line = str(data, encoding='utf8')
            print(line, end='')
            send_log(line, log_url)
        # 进程如果已经退出, 清理
        if process.poll() != None:
            process.stdout.close()
            process.wait(5)
            break
    print('stop ok')
    print('sleep a while')
    time.sleep(command.sleep_time)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Execute test plan')
    # yaml配置文件路径
    parser.add_argument('-f', '--file', type=str, dest='file', help='The yaml config file path')
    # 脚本执行角色，如果单机测试，生产者和消费者在同一个程序测试，选择all，如果生产者不在同一个进程
    parser.add_argument('-r', '--role', type=str, dest='role', help='productor, consumer, or all, default is all')
    # 测试程序,使用官方测试工具还是mo_librabbitmq测试工具
    parser.add_argument('-t', '--type', type=str, dest='prog', help='standard or mo_librabbitmq')
    args = parser.parse_args()

    # 获取配置文件路径
    if not args.file:
        print('config file path not found')
        print_help_and_exit(parser)
    else:
        file = args.file
    # 解析yaml
    config = rmqcfg.parse_yaml(file)
    # 获取角色
    if not args.role:
        role = 'all'
    elif args.role != 'productor' and args.role != 'consumer' and args.role != 'all':
        print('Ther role must be "productor", "consumer", or "all"')
        print_help_and_exit(parser)
    else:
        role = args.role

    # 获取测试主程序, rabbitmq官方测试程序还是mo_librabbitmq库测试程序
    if not args.prog or args.prog not in ['standard', 'mo_librabbitmq']:
        print('The type must be set, value is standard or mo_librabbitmq')
        print_help_and_exit(parser)
    else:
        type = args.prog

    # 获取脚本所在目录
    script_dir = os.path.dirname(__file__)
    result = re.match('^(.*)/\S{1,}/{0,1}$', script_dir)
    os.chdir(result.group(1))
    print('cwd: %s' % os.getcwd())

    task_list = rmqtask.Task.build_task_list(yaml_data=config, role=role)
    if not task_list or len(task_list) == 0:
        print('task list empty')
        sys.exit(-1)

    # 设置日志服务器
    if 'log_server' not in config or not isinstance(config['log_server'], str):
        print('log server not found or type error')
        sys.exit(-1)
    else:
        if re.match(r'^http://[\d\S\.-]+:\d+/?$', config['log_server']):
            LOG_SERVER_URL = re.findall(r'(http://.*:\d+)/?', config['log_server'])[0]
            print(LOG_SERVER_URL)
        else:
            raise ValueError('log server url error')

    # 构造命令行并执行
    for task in task_list:
        command = Command.build_with_task(task, type)
        execute_command(command)