'''
rabbitmq崩溃历史api
'''
import pyrestful.rest
from pyrestful import mediatypes
from pyrestful.rest import get, post, put, delete

class Crash(object):
    node_name = str
    pid = int
    start_time = int
    crash_time = int

class CrashService(pyrestful.rest.RestHandler):
    def initialize(self, database):
        self.database = database

    @post(_path='/nodes/{node_id}/rabbitmq/crashes', _types=[int, dict], _consumes=mediatypes.APPLICATION_JSON, _produces=mediatypes.APPLICATION_JSON)
    def add_crash(self, node_id, crash):
        '''
        添加一条rabbitmq崩溃记录
        :param crash:
        :return:
        '''
        pass

    @get(_path='/nodes/{node_id}/rabbitmq/crashes', _types=[int], _produces=mediatypes.APPLICATION_JSON)
    def get_crashes(self, node_id):
        '''
        获取全部崩溃记录
        :return:
        '''
        pass

    @delete(_path='/nodes/{node_id}/rabbitmq/crashes', _types=[int], _produces=mediatypes.APPLICATION_JSON)
    def clear_crashes(self, node_id):
        '''
        清空崩溃记录
        :return:
        '''
        pass
