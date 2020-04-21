'''
物理服务器资源使用api和rabbitmq服务进程资源使用api
'''
import pyrestful.rest
from pyrestful import mediatypes
from pyrestful.rest import get, post, put, delete
from orm.database import Node, RmqStat, RmqCrash, MachineStat
from sqlalchemy import and_
from error.error import Error
import traceback
import json

class NodeService(pyrestful.rest.RestHandler):
    def initialize(self, database):
        self.database = database

    @post(_path='/nodes', _consumes=mediatypes.TEXT_PLAIN, _produces=mediatypes.APPLICATION_JSON)
    def add_node(self, node_name):
        '''
        添加rabbitmq节点
        :param node_name:
        :return:
        '''
        result = dict()
        try:
            node = Node()
            node.name = node_name
            self.database.add(node)
            self.database.commit()
            result['errno'] = 0
            result['errstr'] = Error.success()
            result['id'] = node.id
        except Exception as err:
            result['errno'] = -1
            result['errstr'] = str(err)
        finally:
            return result


    @delete(_path='/nodes/{node_id}', _types=[int], _produces=mediatypes.APPLICATION_JSON)
    def delete_node(self, node_id):
        '''
        删除rabbitmq节点
        :param node_id:
        :return:
        '''
        result = dict()
        try:
            self.database.query(Node).filter(Node.id == node_id).delete()
            self.database.commit()
            result['errno'] = 0
            result['errstr'] = Error.success()
        except Exception as err:
            result['errno'] = -1
            result['errstr'] = str(err)
        finally:
            return result

    @get(_path='/nodes', _produces=mediatypes.APPLICATION_JSON)
    def get_nodes(self):
        '''
        获取节点列表
        :return:
        '''
        result = dict()
        try:
            nodes = []
            objs = self.database.query(Node).all()
            for obj in objs:
                nodes.append(obj._asdict())
            result['errno'] = 0
            result['errstr'] = Error.success()
            result['result'] = nodes
        except Exception as err:
            result['errno'] = -1
            result['errstr'] = str(err)
        finally:
            return result

    @get(_path='/nodes/{node_id}/name', _types=[int], _produces=mediatypes.APPLICATION_JSON)
    def get_node_name(self, node_id):
        '''
        获取节点名
        :param node_id:
        :return:
        '''
        result = dict()
        try:
            name = self.database.query(Node).filter(Node.id == node_id).first()
            if name == None:
                result['errno'] = -1
                result['errstr'] = Error.data_not_in_db()
            else:
                result['errno'] = 0
                result['errstr'] = Error.success()
                result['name'] = name.name
        except Exception as err:
            result['errno'] = -1
            result['errstr'] = str(err)
        finally:
            return result

    @post(_path='/nodes/{node_id}/rabbitmq/crashes', _consumes=mediatypes.APPLICATION_JSON, _produces=mediatypes.APPLICATION_JSON)
    def add_crash(self, node_id, crash):
        '''
        添加一条rabbitmq崩溃记录
        :param crash:
        :return:
        '''
        result = dict()
        if 'pid' not in crash or 'start_time' not in crash or 'crash_time' not in crash:
            result['errno'] = -1
            result['errstr'] = Error.params_fields_not_found()
            return result
        crash_info = RmqCrash()
        crash_info.node_id = node_id
        crash_info.pid = crash['pid']
        crash_info.start_time = crash['start_time']
        crash_info.crash_time = crash['crash_time']
        try:
            self.database.add(crash_info)
            self.database.commit()
            result['errno'] = 0
            result['errstr'] = Error.success()
            result['id'] = crash_info.id
        except Exception as err:
            result['errno'] = -1
            result['errstr'] = str(err)
        finally:
            return result

    @get(_path='/nodes/{node_id}/rabbitmq/crashes', _produces=mediatypes.APPLICATION_JSON)
    def get_crashes(self, node_id):
        '''
        获取全部崩溃记录
        :return:
        '''
        result = dict()
        try:
            crashes = []
            ret = self.database.query(RmqCrash).filter(RmqCrash.node_id == node_id).order_by(RmqCrash.crash_time.desc()).all()
            for item in ret:
                crashes.append(item._asdict())
            result['errno'] = 0
            result['errstr'] = Error.success()
            result['result'] = crashes
        except Exception as err:
            result['errno'] = -1
            result['errstr'] = str(err)
        finally:
            return result

    @delete(_path='/nodes/{node_id}/rabbitmq/crashes', _types=[int], _produces=mediatypes.APPLICATION_JSON)
    def clear_crashes(self, node_id):
        '''
        清空崩溃记录
        :return:
        '''
        result = dict()
        try:
            self.database.query(RmqCrash).filter(RmqCrash.node_id == node_id).delete()
            self.database.commit()
            result['errno'] = 0
            result['errstr'] = Error.success()
        except Exception as err:
            result['errno'] = -1
            result['errstr'] = str(err)
        finally:
            return result

    @post(_path='/nodes/{node_id}/rabbitmq/resources', _consumes=mediatypes.APPLICATION_JSON, _produces=mediatypes.APPLICATION_JSON)
    def add_rmq_res_stat(self, node_id, res):
        '''
        添加一条rabbitmq资源使用统计
        :param res:
        :return:
        '''
        result = dict()
        if 'stat_time' not in res or 'cpu_usage' not in res or 'mem_usage' not in res or 'disk_spend' not in res or 'msg_summary' not in res:
            result['errno'] = -1
            result['errstr'] = Error.params_fields_not_found()
            return result

        try:
            stat = RmqStat()
            stat.node_id = node_id
            stat.stat_time = res['stat_time']
            stat.cpu_usage = res['cpu_usage']
            stat.mem_usage = res['mem_usage']
            stat.disk_spend = res['disk_spend']
            stat.msg_summary = json.dumps(res['msg_summary'])
            self.database.add(stat)
            self.database.commit()
            result['errno'] = 0
            result['errstr'] = Error.success()
            result['id'] = stat.id
        except Exception as err:
            result['errno'] = -1
            result['errstr'] = str(err)
        finally:
            return result

    @get(_path='/nodes/{node_id}/rabbitmq/resources?<time_from><time_to>', _types=[int, str, str], _produces=mediatypes.APPLICATION_JSON)
    def get_rmq_res_stats(self, node_id, time_from, time_to):
        '''
        获取节点一个时间段内的统计数据
        :param node_id:
        :param time_from:
        :param time_to:
        :return:
        '''
        result = dict()
        try:
            objs = self.database.query(RmqStat).filter(RmqStat.node_id == node_id) \
                .filter(and_(RmqStat.stat_time >= time_from, RmqStat.stat_time < time_to)) \
                .order_by(RmqStat.stat_time.asc()).all()
            ret = []
            for obj in objs:
                ret.append(obj._asdict())
            result['errno'] = 0
            result['errstr'] = Error.success()
            result['result'] = ret
        except Exception as err:
            traceback.print_stack()
            result['errno'] = -1
            result['errstr'] = str(err)
        finally:
            return result

    @delete(_path='/nodes/{node_id}/rabbitmq/resources', _types=[int], _produces=mediatypes.APPLICATION_JSON)
    def delete_node_res_stats(self, node_id):
        '''
        清除一个节点的统计数据
        :param node_id:
        :return:
        '''
        result = dict()
        try:
            self.database.query(RmqStat).filter(RmqStat.node_id == node_id).delete()
            self.database.commit()
            result['errno'] = 0
            result['errstr'] = Error.success()
        except Exception as err:
            result['errno'] = -1
            result['errstr'] = str(err)
        finally:
            return result

    @post(_path='/nodes/{node_id}/machine/resources', _consumes=mediatypes.APPLICATION_JSON, _produces=mediatypes.APPLICATION_JSON)
    def add_machine_stat(self, node_id, res):
        '''
        添加物理服务器统计记录
        :param res:
        :return:
        '''
        result = dict()
        if 'stat_time' not in res or 'cpu_usage' not in res or 'mem_usage' not in res or 'disk_free' not in res:
            result['errno'] = -1
            result['errstr'] = Error.params_fields_not_found()
            return result

        try:
            stat = MachineStat()
            stat.node_id = node_id
            stat.stat_time = res['stat_time']
            stat.cpu_usage = res['cpu_usage']
            stat.mem_usage = res['mem_usage']
            stat.mem_total = res['mem_total']
            stat.disk_free = res['disk_free']
            self.database.add(stat)
            self.database.commit()
            result['errno'] = 0
            result['errstr'] = Error.success()
            result['id'] = stat.id
        except Exception as err:
            result['errno'] = -1
            result['errstr'] = str(err)
        finally:
            return result

    @get(_path='/nodes/{node_id}/machine/resources?<time_from><time_to>', _types=[int, str, str], _produces=mediatypes.APPLICATION_JSON)
    def get_machine_stats(self, node_id, time_from, time_to):
        '''
        获取节点物理服务器统计数据
        :param node_id:
        :param time_from:
        :param time_to:
        :return:
        '''
        result = dict()
        try:
            objs = self.database.query(MachineStat).filter(MachineStat.node_id == node_id) \
                .filter(and_(MachineStat.stat_time >= time_from, MachineStat.stat_time < time_to)) \
                .order_by(MachineStat.stat_time.asc()).all()
            ret = []
            for obj in objs:
                ret.append(obj._asdict())
            result['errno'] = 0
            result['errstr'] = Error.success()
            result['result'] = ret
        except Exception as err:
            traceback.print_stack()
            result['errno'] = -1
            result['errstr'] = str(err)
        finally:
            return result

    @delete(_path='/nodes/{node_id}/machine/resources', _types=[int], _produces=mediatypes.APPLICATION_JSON)
    def delete_machine_stats(self, node_id):
        '''
        删除节点物理服务器统计数据
        :param node_id:
        :return:
        '''
        result = dict()
        try:
            self.database.query(MachineStat).filter(MachineStat.node_id == node_id).delete()
            self.database.commit()
            result['errno'] = 0
            result['errstr'] = Error.success()
        except Exception as err:
            result['errno'] = -1
            result['errstr'] = str(err)
        finally:
            return result