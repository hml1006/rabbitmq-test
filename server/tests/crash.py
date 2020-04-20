import requests
import time
import datetime
import json
import pprint

def add_crash():
    data = {
        'pid': 1228,
        'start_time': int(time.mktime(datetime.datetime.now().timetuple())),
        'crash_time': int(time.mktime(datetime.datetime.now().timetuple())) + 100
    }
    result = requests.post('http://127.0.0.1:8888/nodes/1/rabbitmq/crashes', data=json.dumps(data))
    print('status_code: %d => %s' % (result.status_code, result.reason))
    pprint.pprint(result.text)

def get_crashes():
    result = requests.get('http://127.0.0.1:8888/nodes/1/rabbitmq/crashes')
    print('status_code: %d => %s' % (result.status_code, result.reason))
    print(result.text)

def del_crashes():
    result = requests.delete('http://127.0.0.1:8888/nodes/1/rabbitmq/crashes')
    print('status_code: %d => %s' % (result.status_code, result.reason))
    pprint.pprint(result.text)

if __name__ == '__main__':
    # add_crash()
    # get_crashes()
    del_crashes()