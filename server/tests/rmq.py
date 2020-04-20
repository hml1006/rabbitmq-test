import requests
import time
import datetime
import json
import pprint
import base64

def add_rmq_stat():
    data = {
        'stat_time': int(time.mktime(datetime.datetime.now().timetuple())),
        'cpu_usage': 30,
        'mem_usage': 1000000,
        'disk_spend': 100000,
        'msg_summary': str(base64.b64encode('testtest'.encode(encoding='utf8')), encoding='utf8')
    }
    result = requests.post('http://127.0.0.1:8888/nodes/1/rabbitmq/resources', data=json.dumps(data))
    print('status_code: %d => %s' % (result.status_code, result.reason))
    pprint.pprint(result.text)

def get_rmq_stats():
    result = requests.get('http://127.0.0.1:8888/nodes/1/rabbitmq/resources?time_from=1587364702&time_to=1587364708')
    print('status_code: %d => %s' % (result.status_code, result.reason))
    print(result.text)

def del_rmq_stats():
    result = requests.delete('http://127.0.0.1:8888/nodes/1/rabbitmq/resources')
    print('status_code: %d => %s' % (result.status_code, result.reason))
    pprint.pprint(result.text)

if __name__ == '__main__':
    # add_rmq_stat()
    # get_rmq_stats()
    del_rmq_stats()