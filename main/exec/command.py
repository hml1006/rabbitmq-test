import config.task as rmqtask
from utils.typecheck import typecheck

PROGS = {'standard': 'rabbitmq-perf-test/bin/runjava com.rabbitmq.perf.PerfTest', 'mo_librabbitmq': 'librmq_test/rmqtest'}

class Command:
    def __init__(self):
        # 运行时长, 默认60秒
        self._run_duration = 60
        # 关闭程序超时时间
        self._close_timeout = 60
        self.task = None

    @property
    def type(self):
        return self._type

    @type.setter
    @typecheck(str)
    def type(self, prog_type):
        if prog_type not in PROGS.keys():
            raise ValueError('program type must be standard or mo_librabbitmq')
        self._type = prog_type

    @property
    def prog(self):
        return self._prog

    @prog.setter
    @typecheck(str)
    def prog(self, prog_key):
        if prog_key not in PROGS.keys():
            raise ValueError('program type must be standard or mo_librabbitmq')
        self._prog = PROGS[prog_key]

    @property
    def task_id(self):
        return self._task_id

    @task_id.setter
    @typecheck(str)
    def task_id(self, task_id):
        self._task_id = ' -d %s' % task_id

    @property
    def run_duration(self):
        return self._run_duration

    @run_duration.setter
    @typecheck(int)
    def run_duration(self, run_duration):
        if run_duration <= 0:
            self._run_duration = ''
        self._run_duration = ' -z %d' % run_duration

    @property
    def close_timeout(self):
        return self._close_timeout

    @close_timeout.setter
    @typecheck(int)
    def close_timeout(self, close_timeout):
        if self.type == 'standard':
            self._close_timeout = ' -st %d' % close_timeout
        else:
            self._close_timeout = ' --st %d' % close_timeout

    @property
    def exchange(self):
        return self._exchange

    @exchange.setter
    @typecheck(str)
    def exchange(self, exchange):
        self._exchange = ' -e %s' % exchange

    @property
    def routing_key(self):
        return self._routing_key

    @routing_key.setter
    @typecheck(str)
    def routing_key(self, routing_key):
        self._routing_key = ' -k %s' % routing_key

    @property
    def auto_ack(self):
        return self._auto_ack

    @auto_ack.setter
    @typecheck(bool)
    def auto_ack(self, auto_ack):
        if auto_ack:
            self._auto_ack = ' -a'
        else:
            self._auto_ack = ''

    @property
    def multi_ack(self):
        return self._multi_ack

    @multi_ack.setter
    @typecheck(int)
    def multi_ack(self, multi_ack):
        if multi_ack > 0:
            self._multi_ack = ' -A %d' % multi_ack
        else:
            self._multi_ack = ''

    @property
    def persistent(self):
        return self._persistent

    @persistent.setter
    @typecheck(bool)
    def persistent(self, persistent):
        if persistent:
            self._persistent = ' -f persistent'
        else:
            self._persistent = ''

    @property
    def prefetch(self):
        return self._prefetch

    @prefetch.setter
    @typecheck(int)
    def prefetch(self, prefetch):
        if prefetch > 0:
            self._prefetch = ' -q %d' % prefetch
        else:
            self._prefetch = ''

    @property
    def consumer_rate(self):
        return self._consumer_rate

    @consumer_rate.setter
    @typecheck(int)
    def consumer_rate(self, consumer_rate):
        if consumer_rate > 0:
            self._consumer_rate = ' -R %d' % consumer_rate
        else:
            self._consumer_rate = ''

    @property
    def productor_rate(self):
        return self._productor_rate

    @productor_rate.setter
    @typecheck(int, list)
    def productor_rate(self, productor_rate):
        self._productor_rate = ''
        if isinstance(productor_rate, int):
            if productor_rate > 0:
                self._productor_rate = ' -r %d' % productor_rate
            else:
                self._productor_rate = ''
        elif len(productor_rate) > 0:
            for item in productor_rate:
                if isinstance(item, rmqtask.DynamicProdRate):
                    if self.type == 'standard':
                        item_rate = ' -vr %d:%d' % (item.rate, item.duration)
                    else:
                        item_rate = ' --vr %d:%d' % (item.rate, item.duration)
                    self._productor_rate = self._productor_rate + item_rate

    @property
    def msg_size(self):
        return self._msg_size

    @msg_size.setter
    @typecheck(int, list)
    def msg_size(self, msg_size):
        self._msg_size = ''
        if isinstance(msg_size, int):
            if msg_size > 0:
                self._msg_size = ' -s %d' % msg_size
        elif len(msg_size) > 0:
            for item in msg_size:
                if self.type == 'standard':
                    item_size = ' -vs %d:%d' % (item.size, item.duration)
                else:
                    item_size = ' --vs %d:%d' % (item.size, item.duration)
                self._msg_size = self._msg_size + item_size

    @property
    def sleep_time(self):
        return self._sleep_time

    @sleep_time.setter
    @typecheck(int)
    def sleep_time(self, sleep_time):
        if sleep_time < 0:
            self._sleep_time = 0
        else:
            self._sleep_time = sleep_time

    @property
    def queue(self):
        return self._queue

    @queue.setter
    @typecheck(rmqtask.FixedQueue, rmqtask.DynamicQueue)
    def queue(self, queue):
        if isinstance(queue, rmqtask.FixedQueue):
            self._queue = ' -u %s -x %d -y %d' % (queue.name, queue.productor_num, queue.consumer_num)
        elif isinstance(queue, rmqtask.DynamicQueue):
            if self.type == 'standard':
                self._queue = ' -qp %s -qpf %d -qpt %d -x %d -y %d' % (queue.pattern, queue.queue_from, queue.queue_to, \
                                                                   queue.productor_num, queue.consumer_num)
            else:
                self._queue = ' --qp %s --qpf %d --qpt %d -x %d -y %d' % (queue.pattern, queue.queue_from, queue.queue_to, \
                                                                       queue.productor_num, queue.consumer_num)

    @property
    def url(self):
        return self._url

    @url.setter
    @typecheck(str)
    def url(self, url):
        self._url = ' -h %s' % url

    @property
    def role(self):
        return self._role

    @role.setter
    @typecheck(str)
    def role(self, role):
        self._role = role

    def build_command(self):
        '''
        构造命令行
        :return:
        '''
        if self.role == 'productor':
            args = [self.prog, self.exchange, self.task_id, self.routing_key, self.auto_ack, self.persistent, \
                    self.productor_rate, self.msg_size, self.queue, self.run_duration, self.url]
        elif self.role == 'consumer':
            args = [self.prog, self.exchange, self.task_id, self.routing_key, self.auto_ack, self.prefetch, \
                    self.multi_ack, self.queue, self.consumer_rate, self.run_duration, self.url]
        elif self.role == 'all':
            args = [self.prog, self.exchange, self.task_id, self.routing_key, self.auto_ack, self.multi_ack, \
                    self.persistent, self.prefetch, self.productor_rate, self.consumer_rate, \
                    self.msg_size, self.queue, self.run_duration, self.url]
        else:
            raise ValueError('role error: %s' % self.role)
        return ''.join(args)

    @classmethod
    def build_with_task(cls, task: rmqtask.Task, prog_key):
        command = Command()
        command.prog = prog_key
        command.type = prog_key
        command.role = task.role
        command.exchange = task.exchange
        command.run_duration = task.time
        command.task_id = task.name
        command.routing_key = task.routing_key
        command.auto_ack = task.auto_ack
        command.multi_ack = task.multi_ack
        command.persistent = task.persistent
        command.prefetch = task.prefetch
        command.productor_rate = task.productor_rate
        command.consumer_rate = task.consumer_rate
        command.msg_size = task.msg_size
        command.queue = task.queue
        command.sleep_time = task.sleep_time
        command.url = task.url
        command.task = task
        return command

