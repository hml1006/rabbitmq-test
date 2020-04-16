'''
物理服务器资源使用api和rabbitmq服务进程资源使用api
'''
import pyrestful.rest
from pyrestful import mediatypes
from pyrestful.rest import get, post, put, delete

class RmqStat(object):
    stat_time = int
    cpu_usage = int
    mem_usage = int
    disk_spend = int
    msg_summary = str

class NodeService(pyrestful.rest.RestHandler):
    def initialize(self, database):
        self.database = database

    @post(_path='/nodes', _produces=mediatypes.APPLICATION_JSON)
    def add_node(self, node_name):
        '''
        添加rabbitmq节点
        :param node_name:
        :return:
        '''
        pass

    @delete(_path='/nodes/{node_id}', _types=[int], _produces=mediatypes.APPLICATION_JSON)
    def delete_node(self, node_id):
        '''
        删除rabbitmq节点
        :param node_id:
        :return:
        '''
        pass

    @get(_path='/nodes', _produces=mediatypes.APPLICATION_JSON)
    def get_nodes(self):
        '''
        获取节点列表
        :return:
        '''
        pass

    @get(_path='/nodes/{node_id}/name', _types=[int], _produces=mediatypes.TEXT_PLAIN)
    def get_node_name(self, node_id):
        '''
        获取节点名
        :param node_id:
        :return:
        '''
        pass

class RmqStatService(pyrestful.rest.RestHandler):
    def initialize(self, database):
        self.database = database

    @post(_path='/nodes/{node_id}/rabbitmq/resources', _types=[int, RmqStat], _consumes=mediatypes.APPLICATION_JSON, _produces=mediatypes.APPLICATION_JSON)
    def add_rmq_res_stat(self, node_id, res):
        '''
        添加一条rabbitmq资源使用统计
        :param res:
        :return:
        '''
        pass

    @get(_path='/nodes/{node_id}/rabbitmq/resources?<from><to>', _types=[int, str, str], _produces=mediatypes.APPLICATION_JSON)
    def get_rmq_res_stats(self, node_id, time_from, time_to):
        '''
        获取节点一个时间段内的统计数据
        :param node_id:
        :param time_from:
        :param time_to:
        :return:
        '''
        pass

    @delete(_path='/nodes/{node_id}/rabbitmq/resources', _types=[int], _produces=mediatypes.APPLICATION_JSON)
    def delete_node_res_stats(self, node_id):
        '''
        清除一个节点的统计数据
        :param node_id:
        :return:
        '''
        pass

class MachineStat(object):
    node_id = int
    stat_time = int
    cpu_usage = int
    mem_usage = int
    disk_free = int

class MachineStatService(pyrestful.rest.RestHandler):
    def initialize(self, database):
        self.database = database

    @post(_path='/nodes/{node_id}/machine/resources', _types=[MachineStat], _consumes=mediatypes.APPLICATION_JSON, _produces=mediatypes.APPLICATION_JSON)
    def add_machine_stat(self, res):
        '''
        添加物理服务器统计记录
        :param res:
        :return:
        '''
        pass

    @get(_path='/nodes/{node_id}/machine/resource?<from><to>', _types=[int, str, str], _produces=mediatypes.APPLICATION_JSON)
    def get_machine_stats(self, node_id, time_from, time_to):
        '''
        获取节点物理服务器统计数据
        :param node_id:
        :param time_from:
        :param time_to:
        :return:
        '''
        pass

    @delete(_path='/nodes/{node_id}/machine/resource', _types=[int], _produces=mediatypes.APPLICATION_JSON)
    def delete_machine_stats(self, node_id):
        '''
        删除节点物理服务器统计数据
        :param node_id:
        :return:
        '''
        pass