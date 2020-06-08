import requests
import time
import datetime
import json
import pprint

def add_full():
    data = {
        'stat_time': int(time.mktime(datetime.datetime.now().timetuple())),
        'sent': 1000,
        'received': 500,
        'latency_min': 100,
        'latency_median': 300,
        'latency_75th': 700,
        'latency_95th': 750,
        'latency_99th': 800
    }
    result = requests.post('http://127.0.0.1:8888/tasks/5/task_seqs', data=json.dumps(data))
    print('status_code: %d => %s' % (result.status_code, result.reason))
    pprint.pprint(result.json())

def add_seperate():
    stat_time = int(time.mktime(datetime.datetime.now().timetuple()))
    print(stat_time)

    data = {
        'stat_time': stat_time,
        'received': 500,
        'latency_min': 100,
        'latency_median': 300,
        'latency_75th': 700,
        'latency_95th': 750,
        'latency_99th': 800
    }
    result = requests.post('http://127.0.0.1:8888/tasks/5/task_seqs', data=json.dumps(data))
    print('consumer =================================')
    print('status_code: %d => %s' % (result.status_code, result.reason))
    pprint.pprint(result.text)
    #########################################

    data = {
        'stat_time': stat_time,
        'sent': 1000,
    }
    result = requests.post('http://127.0.0.1:8888/tasks/5/task_seqs', data=json.dumps(data))
    print('producer =================================')
    print('status_code: %d => %s' % (result.status_code, result.reason))
    pprint.pprint(result.text)


def get_seqs():
    result = requests.get('http://127.0.0.1:8888/tasks/5/task_seqs')
    print('status_code: %d => %s' % (result.status_code, result.reason))
    pprint.pprint(result.text)

def del_task_seqs():
    result = requests.delete('http://127.0.0.1:8888/tasks/5/task_seqs')
    print('status_code: %d => %s' % (result.status_code, result.reason))
    pprint.pprint(result.text)

if __name__ == '__main__':
    # add_full()
    # time.sleep(1)
    # add_full()
    # add_seperate()
    # get_seqs()
    del_task_seqs()