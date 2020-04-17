import requests
import time
import datetime
import json
import pprint

def add_task():
    key = int(time.mktime(datetime.datetime.now().timetuple()))
    task = {
        'name': 'task3',
        'key': key,
        'type': 'standard',
        'start_time': key,
        'params': 'xxxxxxxxxxxxxxxxxxxxxx'
    }
    add_task = requests.post('http://127.0.0.1:8888/tasks', data=json.dumps(task))
    print('status_code: %d => %s' % (add_task.status_code, add_task.reason))
    pprint.pprint(add_task.json())

def get_tasks():
    tasks = requests.get('http://127.0.0.1:8888/tasks')
    print('status_code: %d => %s' % (tasks.status_code, tasks.reason))
    pprint.pprint(tasks.json())

def get_task():
    task = requests.get('http://127.0.0.1:8888/tasks/1')
    print('status_code: %d => %s' % (task.status_code, task.reason))
    pprint.pprint(task.json())

def del_task():
    del_task = requests.delete('http://127.0.0.1:8888/tasks/6')
    print('status_code: %d => %s' % (del_task.status_code, del_task.reason))
    pprint.pprint(del_task.json())

if __name__ == '__main__':
    get_tasks()