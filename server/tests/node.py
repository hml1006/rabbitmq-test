import requests
import time
import datetime
import json
import pprint

def add_node1():
    result = requests.post('http://127.0.0.1:8888/nodes', data='louis.localhost')
    print('status_code: %d => %s' % (result.status_code, result.reason))
    pprint.pprint(result.text)

def add_node2():
    result = requests.post('http://127.0.0.1:8888/nodes', data='louis.eth0')
    print('status_code: %d => %s' % (result.status_code, result.reason))
    pprint.pprint(result.text)

def get_nodes():
    result = requests.get('http://127.0.0.1:8888/nodes', data='louis.localhost')
    print('status_code: %d => %s' % (result.status_code, result.reason))
    pprint.pprint(result.text)

def get_node_name():
    result = requests.get('http://127.0.0.1:8888/nodes/1/name', data='louis.localhost')
    print('status_code: %d => %s' % (result.status_code, result.reason))
    pprint.pprint(result.text)

def del_node():
    result = requests.delete('http://127.0.0.1:8888/nodes/4', data='louis.localhost')
    print('status_code: %d => %s' % (result.status_code, result.reason))
    pprint.pprint(result.text)

if __name__ == '__main__':
    # add_node1()
    # add_node2()
    # get_nodes()
    # get_node_name()
    del_node()