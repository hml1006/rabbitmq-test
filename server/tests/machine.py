import requests
import time
import datetime
import json
import pprint
import base64

def add_machine_stat():
    data = {
        'stat_time': int(time.mktime(datetime.datetime.now().timetuple())),
        'cpu_usage': 30,
        'mem_usage': 1000000,
        'disk_free': 100000,
    }
    result = requests.post('http://127.0.0.1:8888/nodes/1/machine/resources', data=json.dumps(data))
    print('status_code: %d => %s' % (result.status_code, result.reason))
    pprint.pprint(result.text)

def get_machine_stats():
    result = requests.get('http://127.0.0.1:8888/nodes/1/machine/resources?time_from=1587369654&time_to=1587369663')
    print('status_code: %d => %s' % (result.status_code, result.reason))
    print(result.text)

def del_machine_stats():
    result = requests.delete('http://127.0.0.1:8888/nodes/1/machine/resources')
    print('status_code: %d => %s' % (result.status_code, result.reason))
    pprint.pprint(result.text)

if __name__ == '__main__':
    # add_machine_stat()
    # get_machine_stats()
    del_machine_stats()