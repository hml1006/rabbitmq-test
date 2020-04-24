import re
from utils.typecheck import typecheck

# role 列表
TASK_ROLES = ['productor', 'consumer', 'all']

class DynamicMsgSize:
    '''
    动态消息大小
    '''
    def __init__(self):
        self._duration = 1
        self._size = 100

    @property
    def duration(self):
        return self._duration

    @duration.setter
    @typecheck(int)
    def duration(self, duration):
        if duration <= 0:
            raise ValueError('duration must bigger than 0')
        self._duration = duration

    @property
    def size(self):
        return self._size

    @size.setter
    @typecheck(int)
    def size(self, size):
        if size <= 0:
            raise ValueError('size must bigger than 0')
        self._size = size

class DynamicProdRate:
    '''
    动态生产者速率
    '''
    def __init__(self):
        self._duration = 1
        self._rate = 100

    @property
    def duration(self):
        return self._duration

    @duration.setter
    @typecheck(int)
    def duration(self, duration):
        if duration <= 0:
            raise ValueError('duration must bigger than 0')
        self._duration = duration

    @property
    def rate(self):
        return self._rate

    @rate.setter
    @typecheck(int)
    def rate(self, rate):
        if rate <= 0:
            raise ValueError('size must bigger than 0')
        self._rate = rate


class DynamicQueue:
    '''
    动态队列
    '''
    def __init__(self):
        # 带通配符的队列名称模式字符串
        self._pattern = ''
        # 队列起始值
        self._queue_from = 0
        # 队列结束值
        self._queue_to = 0
        # 生产者数量
        self._productor_num = 1
        # 消费者数量
        self._consumer_num = 1

    @property
    def pattern(self):
        return self._pattern

    @pattern.setter
    @typecheck(str)
    def pattern(self, pattern):
        if len(pattern) == 0:
            raise ValueError('pattern length must bigger than 0')
        self._pattern = pattern

    @property
    def queue_from(self):
        return self._queue_from

    @queue_from.setter
    @typecheck(int)
    def queue_from(self, queue_from):
        self._queue_from = queue_from

    @property
    def queue_to(self):
        return self._queue_to

    @queue_to.setter
    def queue_to(self, queue_to):
        self._queue_to = queue_to

    @property
    def productor_num(self):
        return self._productor_num

    @productor_num.setter
    @typecheck(int)
    def productor_num(self, productor_num):
        if productor_num <= 0:
            raise ValueError('productor num must bigger than 0')
        self._productor_num = productor_num

    @property
    def consumer_num(self):
        return self._consumer_num

    @consumer_num.setter
    @typecheck(int)
    def consumer_num(self, consumer_num):
        if consumer_num <= 0:
            raise ValueError('consumer num must bigger than 0')
        self._consumer_num = consumer_num

class FixedQueue:
    '''
    固定队列
    '''
    def __init__(self):
        # 队列名
        self._name = ''
        # 生产者数量
        self._productor_num = 1
        # 消费者数量
        self._consumer_num = 1

    @property
    def name(self):
        return self._name

    @name.setter
    @typecheck(str)
    def name(self, name):
        if len(name) == 0:
            raise ValueError('queue name cannot be an empty string')
        self._name = name

    @property
    def productor_num(self):
        return self._productor_num

    @productor_num.setter
    @typecheck(int)
    def productor_num(self, productor_num):
        if productor_num <= 0:
            raise ValueError('productor num must bigger than 0')
        self._productor_num = productor_num

    @property
    def consumer_num(self):
        return self._consumer_num

    @consumer_num.setter
    @typecheck(int)
    def consumer_num(self, consumer_num):
        if consumer_num <= 0:
            raise ValueError('consumer num must bigger than 0')
        self._consumer_num = consumer_num

class Task:
    '''
    测试任务
    '''
    def __init__(self):
        # 任务名
        self._name = ''
        # 单个任务默认测试时间 60秒
        self._time = 60
        # routing-key
        self._routing_key = ''
        # exchange
        self._exchange = ''
        # auto-ack
        self._auto_ack = True
        # multi-ack, 默认每次确认一条消息
        self._multi_ack = 0
        # 消息持久化, 默认关闭
        self._persistent = False
        # perfetch消息预取, 默认每次取1条消息
        self._prefetch = 0
        # 单个生产者速率, 默认100条
        self._productor_rate = 0
        # 单个消费者速率，默认500条
        self._consumer_rate = 0
        # 消息属性列表, key-value
        self._msg_properties = dict()
        # 默认角色
        self._role = 'all'
        # 消息大小
        self._msg_size = 100
        # 消息队列
        self._queue = None
        # 沉睡时间, 执行完一项任务, 休眠一段时间, 等待rabbitmq服务器处理完消息
        # 避免干扰下一个测试任务
        self._sleep_time = 60
        # 服务器地址
        self._url = ''
        # 任务设置信息
        self._config = None

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, yaml_config):
        self._config = yaml_config

    @property
    def name(self):
        return self._name

    @name.setter
    @typecheck(str)
    def name(self, name):
        if len(name) > 0:
            self._name = name
        else:
            raise ValueError('task name cannot be empty')

    @property
    def time(self):
        return self._time

    @time.setter
    @typecheck(int)
    def time(self, time):
        if time > 0:
            self._time = time
        else:
            raise ValueError('time must bigger than 0')

    @property
    def routing_key(self):
        return self._routing_key

    @routing_key.setter
    @typecheck(str)
    def routing_key(self, routing_key):
        if len(routing_key) > 0:
            self._routing_key = routing_key
        else:
            raise ValueError('routing_key cannot be an empty string')

    @property
    def exchange(self):
        return self._exchange

    @exchange.setter
    @typecheck(str)
    def exchange(self, exchange):
        if len(exchange) > 0:
            self._exchange = exchange
        else:
            raise ValueError('exchange cannot be an empty string')

    @property
    def auto_ack(self):
        return self._auto_ack

    @auto_ack.setter
    @typecheck(bool)
    def auto_ack(self, auto_ack):
        self._auto_ack = auto_ack

    @property
    def multi_ack(self):
        return self._multi_ack

    @multi_ack.setter
    @typecheck(int)
    def multi_ack(self, multi_ack):
        if multi_ack > 0:
            self._multi_ack = multi_ack
        else:
            raise ValueError('multi_ack must at least 1')

    @property
    def persistent(self):
        return self._persistent

    @persistent.setter
    @typecheck(bool)
    def persistent(self, persistent):
        self._persistent = persistent

    @property
    def prefetch(self):
        return self._prefetch

    @prefetch.setter
    @typecheck(int)
    def prefetch(self, prefetch):
        if prefetch >= 0:
            self._prefetch = prefetch
        else:
            raise ValueError('prefetch cannot be negative')

    @property
    def productor_rate(self):
        return self._productor_rate

    @productor_rate.setter
    @typecheck(int, list)
    def productor_rate(self, productor_rate):
        self._productor_rate = productor_rate

    @property
    def consumer_rate(self):
        return self._consumer_rate

    @consumer_rate.setter
    @typecheck(int)
    def consumer_rate(self, consumer_rate):
        if consumer_rate <= 0:
            self._consumer_rate = 0
        self._consumer_rate = consumer_rate

    @property
    def msg_properties(self):
        return self._msg_properties

    @msg_properties.setter
    @typecheck(dict)
    def msg_properties(self, msg_properties):
        self._msg_properties = msg_properties

    @property
    def role(self):
        return self._role

    @role.setter
    @typecheck(str)
    def role(self, role):
        '''
        设置任务角色, 只作为生产者或消费者, 或者二者兼有
        :param role: productor, consumer, all
        :return:
        '''
        if role in TASK_ROLES:
            self._role = role
        else:
            raise ValueError('Role must be in "productor" "consumer" "all"')

    @property
    def msg_size(self):
        return self._msg_size

    @msg_size.setter
    @typecheck(int, list)
    def msg_size(self, msg_size):
        if isinstance(msg_size, int) and msg_size <= 0:
            raise ValueError('msg size must bigger than 0')
        self._msg_size = msg_size

    @property
    def queue(self):
        return self._queue

    @queue.setter
    @typecheck(FixedQueue, DynamicQueue)
    def queue(self, queue):
        self._queue = queue

    @property
    def sleep_time(self):
        return self._sleep_time

    @sleep_time.setter
    @typecheck(int)
    def sleep_time(self, sleep_time):
        if sleep_time >= 0:
            self._sleep_time = sleep_time
        else:
            raise ValueError('sleep time cannot be negative')

    @property
    def url(self):
        return self._url

    @url.setter
    @typecheck(str)
    def url(self, url):
        if len(url) > 0 and re.match('^amqp:\/\/\S*:[0-9]{2,5}\/{0,1}$', url):
            self._url = url
        else:
            raise ValueError('url must not be empty and should like "amqp://localhost:5671"')


    @classmethod
    def build_task(cls, yaml_task: dict, role: str, url: str, sleep_time: int = 0):
        '''
        把yaml配置中的task转换为Task对象
        :param yaml_task:
        :param role:
        :return:
        '''
        if not yaml_task:
            raise ValueError('yaml task empty')
        task = Task()
        print(yaml_task['name'])
        task.config = yaml_task
        task.name = yaml_task['name']
        task.time = yaml_task['time']
        task.exchange = yaml_task['exchange']
        task.role = role
        if 'routing-key' in yaml_task:
            task.routing_key = yaml_task['routing-key']
        else:
            raise ValueError('if role is productor or consumer, routing-key must be set')
        if 'auto-ack' in yaml_task:
            task.auto_ack = yaml_task['auto-ack']
        if 'multi-ack' in yaml_task:
            task.multi_ack = yaml_task['multi-ack']
        if 'persistent' in yaml_task:
            task.persistent = yaml_task['persistent']
        if 'prefetch' in yaml_task:
            task.prefetch = yaml_task['prefetch']
        if 'consumer-rate' in yaml_task:
            task.consumer_rate = yaml_task['consumer-rate']

        # 生产者速率需要判断是否是动态速率
        if 'productor-rate' in yaml_task:
            rate = yaml_task['productor-rate']
            if isinstance(rate, int): # 固定速率
                task.productor_rate = rate
            elif isinstance(rate, list):
                rate_list = []
                for dynamic_rate in rate:
                    if 'duration' in dynamic_rate and 'rate' in dynamic_rate:
                        dynamic_rate_obj = DynamicProdRate()
                        dynamic_rate_obj.duration = dynamic_rate['duration']
                        dynamic_rate_obj.rate = dynamic_rate['rate']
                        rate_list.append(dynamic_rate_obj)
                    else:
                        raise ValueError('duration or rate not found in productor-rate object')
                if len(rate_list) != 0:
                    task.productor_rate = rate_list
            else:
                raise ValueError('please check productor-rate field')

        # 需要检查是否是动态消息大小
        if 'msg-size' in yaml_task:
            msg_size = yaml_task['msg-size']
            if isinstance(msg_size, int):
                task.msg_size = msg_size
            elif isinstance(msg_size, list):
                size_list = []
                for item in msg_size:
                    if 'duration' in item and 'size' in item:
                        msg_size_obj = DynamicMsgSize()
                        msg_size_obj.duration = item['duration']
                        msg_size_obj.size = item['size']
                        size_list.append(msg_size_obj)
                    else:
                        raise ValueError('duration or size not found in msg-size')
                if len(size_list) != 0:
                    task.msg_size = size_list
            else:
                raise ValueError('please check msg-size field')
        # 消息属性
        if 'msg-prroperties' in yaml_task:
            properties = yaml_task['msg-properties']
            if len(properties) > 0:
                msg_properties = dict()
                for (k, v) in properties:
                    msg_properties[k] = v
                task.msg_properties = msg_properties
        # 获取队列信息
        if 'queue' in yaml_task:
            queue = yaml_task['queue']
            queue_obj = None
            # 包含pattern字段，是动态队列
            if 'pattern' in queue:
                queue_obj = DynamicQueue()
                queue_obj.pattern = queue['pattern']
                if 'from' in queue and 'to' in queue:
                    queue_obj.queue_from = queue['from']
                    queue_obj.queue_to = queue['to']
                else:
                    raise ValueError('from or to field not found in queue')
            else:
                queue_obj = FixedQueue()
                if 'name' in queue:
                    queue_obj.name = queue['name']
                else:
                    raise ValueError('name field not found in queue')
            task.queue = queue_obj
        # 设置url
        if not url or len(url) == 0 or not isinstance(url, str):
            raise ValueError('url not working')
        else:
            task.url = url
        task.sleep_time = sleep_time
        return task

    @classmethod
    def build_task_list(cls, yaml_data, role):
        '''
        通过解析后的yaml数据构造任务列表
        :param yaml_data: yaml结构
        :param role: productor, consumer, all其中一个
        :return:
        '''
        if role not in TASK_ROLES:
            raise ValueError('role must in %s' % (TASK_ROLES))
        url = yaml_data['url']
        if not url or len(url) == 0:
            raise ValueError('url error')
        sleep = yaml_data['sleep']
        if not sleep:
            raise ValueError('duration error')
        task_list = yaml_data['task-list']
        if not task_list or len(task_list) == 0:
            raise ValueError('task list empty')

        # 任务列表
        tasks = []
        for task in task_list:
            instance = Task.build_task(task, role, url, sleep)
            tasks.append(instance)
        return tasks
