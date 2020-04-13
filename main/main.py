import argparse
import sys
from .config import config

def print_help_and_exit(parser):
    '''
    打印帮助信息并退出程序
    :param parser:
    :return:
    '''
    parser.print_help()
    sys.exit(-1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Execute test plan')
    # yaml配置文件路径
    parser.add_argument('-f', '--file', type=str, dest='file', help='The yaml config file path')
    # 脚本执行角色，如果单机测试，生产者和消费者在同一个程序测试，选择all，如果生产者不在同一个进程
    parser.add_argument('-r', '--role', type=str, dest='role', help='productor, consumer, or all， default is all')
    args = parser.parse_args()

    # 获取配置文件路径
    if not args.file:
        print('config file path not found')
        parser.print_help()
    else:
        file = args.file
    
    # 获取角色
    if not args.role:
        role = 'all'
    elif args.role != 'productor' and args.role != 'consumer' and args.role != 'all':
        print('Ther role must be "productor", "consumer", or "all"')
        parser.print_help()
    else:
        role = args.role

    config = config.parse_yaml(file)