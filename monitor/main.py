'''
监控脚本主程序
'''
import time
import sys
import argparse
import requests
from mthread.pick import PickRmqThread, PickMachineThread
from config.config import Config
from utils.common import get_node_name

def get_nodes():
    config = Config.get_instance()
    url = 'http://%s:%d/nodes' % (config.collect_host, config.collect_port)
    result = requests.get(url)
    if result.status_code != 200:
        raise Exception('error occurs')
    msg = result.json()
    if 'errno' in msg:
        if msg['errno'] == 0:
            return msg['result']
        else:
            print('errstr: %s' % msg['errstr'])
    raise Exception('error: %s' % result.text)

def add_node(node_name):
    '''
    添加节点并返回id
    :param node_name:
    :return:
    '''
    config = Config.get_instance()
    url = 'http://%s:%d/nodes' % (config.collect_host, config.collect_port)
    result = requests.post(url, data=node_name)
    if result.status_code != 200:
        raise Exception('error occurs')
    msg = result.json()
    if 'errno' in msg:
        if msg['errno'] == 0:
            return msg['id']
        else:
            print('errstr: %s' % msg['errstr'])
    raise Exception('error: %s' % result.text)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', dest='path', help='Config file path')
    args = parser.parse_args()
    if args.path == None:
        print('config file not found')
        parser.print_help()
        sys.exit(-1)

    # 初始化配置
    Config.init(args.path)

    # 添加节点信息或者查询添加后的节点信息
    node_name = get_node_name()
    if not node_name:
        print('node name not found')
        sys.exit(-1)

    config = Config.get_instance()
    nodes = get_nodes()
    # 检查节点是否已经存在
    is_added = False
    for node in nodes:
        if node_name == node['name']:
            is_added = True
            config.node_id = node['id']

    # 节点不存在,则添加
    if is_added == False:
        node_id = add_node(node_name)
        if node_id != None:
            config.node_id = node_id
        else:
            print('add node failed')
            sys.exit(-1)

    # 开启rmq信息采集线程
    pick_rmq_thread = PickRmqThread()
    pick_rmq_thread.start()

    # 开启物理服务器信息采集
    pick_machine_thread = PickMachineThread()
    pick_machine_thread.start()

    while True:
        time.sleep(1000)
