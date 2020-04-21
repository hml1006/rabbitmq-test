'''
资源信息采集线程, 采集rmq服务资源使用情况和物理服务器资源使用情况, rmq服务统计信息, 并发送给消息通信线程
'''
import threading
import time
import datetime
import requests
import json
import traceback
import psutil
from rabbitmq_admin import AdminAPI
from utils.common import get_rmq_process, get_rmq_process_mem_usage, get_machine_mem_info
from config.config import Config
from utils.disk import get_file_size, get_dist_free

# rabbitmq 数据目录
RABBIT_DATA_DIR = '/opt/data/rabbitmq'

class PickRmqThread(threading.Thread):
    def __init__(self, daemon = True):
        super().__init__()
        self.setName('pickrmq')
        self.setDaemon(daemon)
        print('create thread: %s' % self.name)

        self.__rabbitmq_api = None
        self.__session = requests.Session()

    def run(self) -> None:
        process = None
        while True:
            try:
                if process == None:
                    print('rabbitmq not start')
                    process = get_rmq_process()
                    if process == None:
                        time.sleep(5)
                        continue

                if not process.is_running():
                    self.send_crash(process)
                    process = None
                    continue
                else:
                    # 内存占用, 单位 MB
                    mem_usage = get_rmq_process_mem_usage(process)
                    # 磁盘空间占用, 单位 MB
                    disk_spend = get_file_size(RABBIT_DATA_DIR)
                    # cpu使用率, 统计间隔5秒, 会导致5秒阻塞
                    cpu_percent = process.cpu_percent(interval=5)
                    # 统计时间
                    stat_time = int(time.mktime(datetime.datetime.now().timetuple()))
                    data = {
                        'stat_time': stat_time,
                        'cpu_usage': cpu_percent,
                        'mem_usage': mem_usage,
                        'disk_spend': disk_spend,
                        'msg_summary': self.get_rabbitmq_stats()
                    }
                    self.send_stat_report(data)
            except Exception as err:
                print(err)
                traceback.print_stack()

    def get_rabbitmq_stats(self):
        if self.__rabbitmq_api == None:
            config = Config.get_instance()
            url = 'http://%s:%d' % (config.rmq_host, config.rmq_port)
            self.__rabbitmq_api = AdminAPI(url=url, auth=(config.rmq_user, config.rmq_password))
        overview = self.__rabbitmq_api.overview()
        ready = 0
        unacked = 0
        total = 0
        publish_rate = 0
        deliver_manual_ack = 0
        consumer_ack = 0
        disk_read = 0
        disk_write = 0
        if overview == None:
            print('get rabbitmq overview failed')
            return None
        if 'queue_totals' in overview:
            queue_totals = overview['queue_totals']
            if 'messages' in queue_totals:
                total = queue_totals['messages']
            if 'messages_ready' in queue_totals:
                ready = queue_totals['messages_ready']
            if 'messages_unacknowledged' in queue_totals:
                unacked = queue_totals['messages_unacknowledged']
        if 'message_stats' in overview:
            message_stats = overview['message_stats']
            if 'publish_details' in message_stats:
                publish_details = message_stats['publish_details']
                if 'rate' in publish_details:
                    publish_rate = publish_details['rate']
            if 'deliver_details' in message_stats:
                deliver_details = message_stats['deliver_details']
                if 'rate' in deliver_details:
                    deliver_manual_ack = deliver_details['rate']
            if 'ack_details' in message_stats:
                ack_details = message_stats['ack_details']
                if 'rate' in ack_details:
                    consumer_ack = ack_details['rate']
            if 'disk_reads_details' in message_stats:
                disk_reads_details = message_stats['disk_reads_details']
                if 'rate' in disk_reads_details:
                    disk_read = disk_reads_details['rate']
            if 'disk_writes_details' in message_stats:
                disk_writes_details = message_stats['disk_writes_details']
                if 'rate' in disk_writes_details:
                    disk_write = disk_writes_details['rate']

            return {
                'total': total,
                'ready': ready,
                'unacked': unacked,
                'publish_rate': publish_rate,
                'deliver_manual_ack': deliver_manual_ack,
                'consumer_ack': consumer_ack,
                'disk_read': disk_read,
                'disk_write': disk_write
            }

    def send_stat_report(self, data):
        config = Config.get_instance()
        url = 'http://%s:%d/nodes/%d/rabbitmq/resources' % (config.collect_host, config.collect_port, config.node_id)
        result = self.__session.post(url=url, data=json.dumps(data))
        if result.status_code == 200:
            obj = result.json()
            if obj['errno'] == 0:
                print('add rabbitmq stat report success')
            else:
                print('add rabbitmq stat report failed: %s' % obj['errstr'])
        else:
            print('add rabbitmq stat report failed ==>')
            print('status => %d, errstr: %s' % (result.status_code, result.text))

    def send_crash(self, process):
        '''
        发送进程崩溃报告
        :param process:
        :return:
        '''
        if process == None:
            print('process None')
            return None
        start_time = process.create_time()
        crash_time = int(time.mktime(datetime.datetime.now().timetuple()))
        pid = process.pid
        config = Config.get_instance()
        url = 'http://%s:%d/nodes/%d/rabbitmq/crashes' % (config.collect_host, config.collect_port, config.node_id)
        data = {
            'pid': pid,
            'start_time': start_time,
            'crash_time': crash_time
        }
        result = self.__session.post(url=url, data=json.dumps(data))
        if result.status_code == 200:
            obj = result.json()
            if obj['errno'] == 0:
                print('add rabbitmq crash report success')
            else:
                print('add rabbitmq crash report failed: %s' % obj['errstr'])
        else:
            print('add rabbitmq crash report failed ==>')
            print('status => %d, errstr: %s' % (result.status_code, result.text))

class PickMachineThread(threading.Thread):
    def __init__(self, daemon=True):
        super().__init__()
        self.setName('pickmachine')
        self.setDaemon(daemon)
        print('create thread: %s' % self.name)

        self.__session = requests.Session()

    def run(self) -> None:
        while True:
            try:
                mem_usage, mem_total = get_machine_mem_info()
                disk_free = get_dist_free(RABBIT_DATA_DIR)
                cpu_usage = psutil.cpu_percent(interval=5)
                stat_time = int(time.mktime(datetime.datetime.now().timetuple()))

                data = {
                    'stat_time': stat_time,
                    'cpu_usage': cpu_usage,
                    'mem_usage': mem_usage,
                    'mem_total': mem_total,
                    'disk_free': disk_free
                }
                self.send_stat_report(data)
            except Exception as err:
                print(err)
                traceback.print_stack()

    def send_stat_report(self, data):
        config = Config.get_instance()
        url = 'http://%s:%d/nodes/%d/machine/resources' % (config.collect_host, config.collect_port, config.node_id)
        result = self.__session.post(url=url, data=json.dumps(data))
        if result.status_code == 200:
            obj = result.json()
            if obj['errno'] == 0:
                print('add machine stat report success')
            else:
                print('add machine stat report failed: %s' % obj['errstr'])
        else:
            print('add machine stat report failed ==>')
            print('status => %d, errstr: %s' % (result.status_code, result.text))