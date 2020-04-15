import argparse
import sys
import os
import re
import subprocess
import time
import config.config as rmqcfg
import config.task as rmqtask
from exec.command import Command

# 全局日志配置
LOG_SERVER_URL = None

def print_help_and_exit(parser):
    '''
    打印帮助信息并退出程序
    :param parser:
    :return:
    '''
    parser.print_help()
    sys.exit(-1)

def send_log(line):
    '''
    把行日志提取有效数据并发送到日志服务器
    :param line:
    :return:
    '''
    pass

def execute_command(command: Command):
    # 构造命令
    command_line = command.build_command()
    print('command: %s' % command_line)
    # 执行命令
    process = subprocess.Popen(command_line, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, close_fds=True)
    if not process:
        raise Exception('cannot execute command')
    while True:
        data = process.stdout.readline()
        if data and len(data) > 0:
            print(str(data, encoding='utf8'), end='')
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

    # 获取脚本所在目录
    script_dir = os.path.dirname(__file__)
    script_dir = '/home/louis/code/rabbitmq-test/main'
    result = re.match('^(.*)/\S{1,}/{0,1}$', script_dir)
    os.chdir(result.group(1))
    print('cwd: %s' % os.getcwd())

    # 获取配置文件路径
    if not args.file:
        print('config file path not found')
        print_help_and_exit(parser)
    else:
        file = args.file
    
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

    # 解析yaml
    config = rmqcfg.parse_yaml(file)
    task_list = rmqtask.Task.build_task_list(yaml_data=config, role=role)
    if not task_list or len(task_list) == 0:
        print('task list empty')
        sys.exit(-1)

    # 设置日志服务器
    if 'log_server' not in config:
        print('log server not found')
        sys.exit(-1)
    else:
        LOG_SERVER_URL = config['log_server']

    # 构造命令行并执行
    for task in task_list:
        command = Command.build_with_task(task, type)
        execute_command(command)