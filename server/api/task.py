'''
测试任务和测试统计序列api
'''
import pyrestful.rest
from pyrestful import mediatypes
from pyrestful.rest import get, post, delete
from error.error import Error
from orm.database import Task as OrmTask, TaskSeq
import json

class Task(object):
    name = str
    key = int
    type = str
    start_time = int
    params = str

class TaskService(pyrestful.rest.RestHandler):
    def initialize(self, database):
        self.database = database

    @post(_path='/tasks', _consumes=mediatypes.APPLICATION_JSON, _produces=mediatypes.APPLICATION_JSON)
    def add_task(self, task):
        '''
        创建测试任务
        :param task:
        :return:
        '''
        result = dict()
        if 'name' not in task or 'key' not in task or 'type' not in task or 'start_time' not in task or 'params' not in task:
            result['errno'] = -1
            result['errstr'] = Error.params_fields_not_found()
            return result
        # 先检查任务是否存在
        try:
            find_task = self.database.query(OrmTask).filter_by(name = task['name']).first()
            # key不同,说明不是子任务,属于重复添加
            if find_task != None and find_task.key != task['key']:
                result['errno'] = -1
                result['errstr'] = Error.task_exists()
                return result
            # key相同,说明是子任务,不需要再添加,返回成功
            if find_task != None and find_task.key == task['key']:
                result['errno'] = 0
                result['task_id'] = find_task.id
                result['errstr'] =Error.success()
                return result
        except Exception as err:
            print(err)
            result['errno'] = -1
            result['errstr'] = str(err)
            return result

        # 任务不存在,添加
        db_task = OrmTask()
        db_task.name = task['name']
        db_task.key = task['key']
        db_task.type = task['type']
        db_task.start_time = task['start_time']
        db_task.params = task['params']
        try:
            self.database.add(db_task)
            self.database.commit()
            result['errno'] = 0
            result['id'] = db_task.id
            result['errstr'] = Error.success()
        except Exception as err:
            result['errno'] = -1
            result['errstr'] = str(err)
        finally:
            return result

    @delete(_path='/tasks/{task_id}', _types=[int], _produces=mediatypes.APPLICATION_JSON)
    def delete_task(self, task_id):
        '''
        删除测试任务
        :param task_id:
        :return:
        '''
        result = dict()
        try:
            self.database.query(TaskSeq).filter(TaskSeq.task_id == task_id).delete()
            self.database.query(OrmTask).filter(OrmTask.id == task_id).delete()
            self.database.commit()
            result['errno'] = 0
            result['errstr'] = Error.success()
        except Exception as err:
            result['errno'] = -1
            result['errstr'] = str(err)
        finally:
            return result

    @get(_path='/tasks', _produces=mediatypes.APPLICATION_JSON)
    def get_tasks(self):
        '''
        获取测试任务列表
        :return:
        '''
        result = dict()
        try:
            tasks = self.database.query(OrmTask).order_by(OrmTask.start_time.desc()).all()
            task_list = []
            for task in tasks:
                dict_task = task._asdict()
                task_list.append(dict_task)
            result['errno'] = 0
            result['errstr'] = Error.success()
            result['result'] = task_list
        except Exception as err:
            print(err)
            result['errno'] = -1
            result['errstr'] = str(err)
        finally:
            return result

    @get(_path='/tasks/{task_id}', _produces=mediatypes.APPLICATION_JSON)
    def get_task(self, task_id):
        '''
        获取测试任务详情
        :param task_id:
        :return:
        '''
        result = dict()
        try:
            task = self.database.query(OrmTask).filter(OrmTask.id == task_id).first()
            if not task:
                self.set_status(404, Error.task_not_exists())
                result['errno'] = -1
                result['errstr'] = Error.task_not_exists()
            if task:
                result['errno'] = 0
                result['errstr'] = Error.success()
                result['result'] = task._asdict()
        except Exception as err:
            result['errno'] = -1
            result['errstr'] = str(err)
        finally:
            return result

    @post(_path='/tasks/{task_id}/task_seqs', _consumes=mediatypes.APPLICATION_JSON, _produces=mediatypes.APPLICATION_JSON)
    def add_task_seq(self, task_id, seq):
        '''
        添加任务指标统计序列
        :param seq:
        :return:
        '''
        result = dict()
        # 如果不存在统计时间,则参数错误
        if seq['stat_time'] == None:
            result['errno'] = -1
            result['errstr'] = Error.params_fields_not_found()
            return result
        # 生产者消费者在同一个进程情况
        if 'sent' in seq and 'received' in seq:
            try:
                task_seq = TaskSeq()
                task_seq.task_id = task_id
                task_seq.stat_time = seq['stat_time']
                task_seq.sent = seq['sent']
                task_seq.received = seq['received']
                task_seq.latency_min = seq['latency_min']
                task_seq.latency_median = seq['latency_median']
                task_seq.latency_75th = seq['latency_75th']
                task_seq.latency_95th = seq['latency_95th']
                task_seq.latency_99th = seq['latency_99th']
                self.database.add(task_seq)
                self.database.commit()
                result['errno'] = 0
                result['errstr'] = Error.success()
            except Exception as err:
                result['errno'] = -1
                result['errstr'] = str(err)
        # 生产者消费者分离模式下的生产者
        elif 'sent' in seq and 'received' not in seq:
            sql = 'insert into task_seq(task_id,stat_time,sent) values(%s,%d,%d) ON DUPLICATE KEY UPDATE sent=sent+%d' % \
                  (task_id, int(seq['stat_time']), seq['sent'], seq['sent'])
            try:
                self.database.execute(sql)
                self.database.commit()
                result['errno'] = 0
                result['errstr'] = Error.success()
            except Exception as err:
                result['errno'] = -1
                result['errstr'] = str(err)
        # 分离模式下的消费者上报数据
        elif 'sent' not in seq and 'received' in seq:
            sql = 'insert into task_seq(task_id,stat_time,received,latency_min,latency_median,latency_75th,latency_95th,latency_99th) ' \
                  'values(%s,%d,%d,%d,%d,%d,%d,%d) ON DUPLICATE KEY UPDATE received=received+%d,latency_min=%d,latency_median=%d,latency_75th=%d,' \
                  'latency_95th=%d,latency_99th=%d'% \
                  (task_id, int(seq['stat_time']), seq['received'], seq['latency_min'], seq['latency_median'], seq['latency_75th'], seq['latency_95th'], seq['latency_99th'], \
                   seq['received'], seq['latency_min'], seq['latency_median'], seq['latency_75th'], seq['latency_95th'], seq['latency_99th'])
            try:
                self.database.execute(sql)
                self.database.commit()
                result['errno'] = 0
                result['errstr'] = Error.success()
            except Exception as err:
                result['errno'] = -1
                result['errstr'] = str(err)
        else:
            result['errno'] = -1
            result['errstr'] = Error.params_fields_not_found()

        return result

    @get(_path='/tasks/{task_id}/task_seqs', _types=[int], _produces=mediatypes.APPLICATION_JSON)
    def get_task_seqs(self, task_id):
        '''
        获取任务的全部指标统计序列
        :param task_id:
        :return:
        '''
        result = dict()
        try:
            seqs = self.database.query(TaskSeq).filter(TaskSeq.task_id == task_id).order_by(TaskSeq.stat_time.asc()).all()
            items = []
            for seq in seqs:
                items.append(seq._asdict())
            result['errno'] = 0
            result['errstr'] = Error.success()
            result['result'] = items
        except Exception as err:
            result['errno'] = -1
            result['errstr'] = str(err)
        finally:
            return result

    @delete(_path='/tasks/{task_id}/task_seqs', _types=[int], _produces=mediatypes.APPLICATION_JSON)
    def delete_task_seqs(self, task_id):
        '''
        删除任务统计序列
        :param task_id:
        :return:
        '''
        result = dict()
        try:
            self.database.query(TaskSeq).filter(TaskSeq.task_id == task_id).delete()
            self.database.commit()
            result['errno'] = 0
            result['errstr'] = Error.success()
        except Exception as err:
            result['errno'] = -1
            result['errstr'] = str(err)
        finally:
            return result
