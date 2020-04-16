'''
测试任务和测试统计序列api
'''
import pyrestful.rest
from pyrestful import mediatypes
from pyrestful.rest import get, post, delete
from error.error import Error
import orm.database
import json

class Task(object):
    name = str
    key = int
    type = str
    start_time = int
    params = str

class TaskStatSeq(object):
    task_id = int
    stat_time = int
    sent = int
    received = int
    latency_min = int
    latency_median = int
    latency_75th = int
    latency_95th = int
    latency_99th = int

class TaskService(pyrestful.rest.RestHandler):
    def initialize(self, database):
        self.database = database

    @post(_path='/tasks', _types=[Task], _consumes=mediatypes.APPLICATION_JSON, _produces=mediatypes.APPLICATION_JSON)
    def add_task(self, task):
        '''
        创建测试任务
        :param task:
        :return:
        '''
        result = dict()
        if 'name' not in task or 'key' not in task or 'type' not in task or 'start_time' not in task or 'params' not in task:
            result['errno'] = -1
            result['errstr'] = Error.json_fields_not_found()
            return result
        # 先检查任务是否存在
        find_task = self.database.query(orm.database.Task).filter(orm.database.Task.name == task['name']).first()
        # key不同,说明不是子任务,属于重复添加
        if find_task != None and find_task.key != task['key']:
            result['errno'] = -1
            result['errstr'] = Error.task_exists()
        # key相同,说明是子任务,不需要再添加,返回成功
        if find_task != None and find_task.key == task['key']:
            result['errno'] = 0
            result['task_id'] = find_task.id
            result['errstr'] =Error.success()
            return result

        # 任务不存在,添加
        db_task = orm.database.Task()
        db_task.name = task['name']
        db_task.key = task['key']
        db_task.type = task['type']
        db_task.start_time = task['start_time']
        db_task.params = task['params']
        self.database.add(db_task)
        self.database.commit()
        result['errno'] = 0
        result['id'] = db_task.id
        result['errstr'] = Error.success()
        return result

    @delete(_path='/tasks/{task_id}', _types=[int], _produces=mediatypes.APPLICATION_JSON)
    def delete_task(self, task_id):
        '''
        删除测试任务
        :param task_id:
        :return:
        '''
        self.database.query(orm.database.Task).filter(orm.database.Task.id == task_id).delete()
        result = dict()
        result['errno'] = 0
        result['errstr'] = Error.success()
        return result

    @get(_path='/tasks', _produces=mediatypes.APPLICATION_JSON)
    def get_tasks(self):
        '''
        获取测试任务列表
        :return:
        '''
        tasks = self.database.query(orm.database.Task).order_by(orm.database.Task.start_time).desc().all()
        return tasks

    @get(_path='/tasks/{task_id}', _produces=mediatypes.APPLICATION_JSON)
    def get_task(self, task_id):
        '''
        获取测试任务详情
        :param task_id:
        :return:
        '''
        result = dict()
        task = self.database.query(orm.database.Task).filter(orm.database.Task.id == task_id).first()
        if task == None:
            self.set_status(404, Error.task_not_exists())
            result['errno'] = -1
            result['errstr'] = Error.task_not_exists()
            return result
        return task


class TaskStatSeqService(pyrestful.rest.RestHandler):
    def initialize(self, database):
        self.database = database

    @post(_path='/tasks/{task_id}/task_seqs', _types=[TaskStatSeq], _consumes=mediatypes.APPLICATION_JSON, _produces=mediatypes.APPLICATION_JSON)
    def add_task_seq(self, seq):
        '''
        添加任务指标统计序列
        :param seq:
        :return:
        '''
        pass

    @get(_path='/tasks/{task_id}/task_seqs', _types=[int], _produces=mediatypes.APPLICATION_JSON)
    def get_task_seqs(self, task_id):
        '''
        获取任务的全部指标统计序列
        :param task_id:
        :return:
        '''
        pass

    @delete(_path='/tasks/{task_id}/task_seqs', _types=[int], _produces=mediatypes.APPLICATION_JSON)
    def delete_task_seqs(self, task_id):
        '''
        删除任务统计序列
        :param task_id:
        :return:
        '''
        pass