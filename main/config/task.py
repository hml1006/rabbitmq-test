from utils.typecheck import typecheck

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
    def set_duration(self, duration):
        if duration <= 0:
            raise ValueError('duration must bigger than 0')
        self._duration = duration

    @property
    def size(self):
        return self._size

    @size.setter
    @typecheck(int)
    def set_size(self, size):
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
    def set_duration(self, duration):
        if duration <= 0:
            raise ValueError('duration must bigger than 0')
        self._duration = duration

    @property
    def size(self):
        return self._size

    @size.setter
    @typecheck(int)
    def set_size(self, size):
        if size <= 0:
            raise ValueError('size must bigger than 0')
        self._size = size


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
    def set_pattern(self, pattern):
        if len(pattern) == 0:
            raise ValueError('pattern length must bigger than 0')
        self._pattern = pattern

    @property
    def queue_from(self):
        return self._queue_from

    @queue_from.setter
    @typecheck(int)
    def set_queue_from(self, queue_from):
        self._queue_from = queue_from

    @property
    def queue_to(self):
        return self._queue_to

    @queue_to.setter
    def set_queue_to(self, queue_to):
        self._queue_to = queue_to

    @property
    def productor_num(self):
        return self._productor_num

    @productor_num.setter
    @typecheck(int)
    def set_productor_num(self, productor_num):
        if productor_num <= 0:
            raise ValueError('productor num must bigger than 0')
        self._productor_num = productor_num

    @property
    def consumer_num(self):
        return self._consumer_num

    @consumer_num.setter
    @typecheck(int)
    def set_consumer_num(self, consumer_num):
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
    def set_name(self, name):
        if len(name) == 0:
            raise ValueError('queue name cannot be an empty string')
        self._name = name

    @property
    def productor_num(self):
        return self._productor_num

    @productor_num.setter
    @typecheck(int)
    def set_productor_num(self, productor_num):
        if productor_num <= 0:
            raise ValueError('productor num must bigger than 0')
        self._productor_num = productor_num

    @property
    def consumer_num(self):
        return self._consumer_num

    @consumer_num.setter
    @typecheck(int)
    def set_consumer_num(self, consumer_num):
        if consumer_num <= 0:
            raise ValueError('consumer num must bigger than 0')
        self._consumer_num = consumer_num

class Task:
    '''
    测试任务
    '''
    def __init__(self):
        # 单个任务默认测试时间 60秒
        self._time = 60
        # routing-key
        self._routing_key = ''
        # exchange
        self._exchange = ''
        # auto-ack
        self._auto_ack = True
        # multi-ack, 默认每次确认一条消息
        self._multi_ack = 1
        # 消息持久化, 默认关闭
        self._persistent = False
        # perfetch消息预取, 默认每次取1条消息
        self._prefetch = 1
        # 单个生产者速率, 默认100条
        self._productor_rate = 100
        # 单个消费者速率，默认500条
        self._consumer_rate = 500
        # 消息属性列表, key-value
        self._msg_properties = dict()
        # 默认角色
        self._role = 'all'
        # 消息大小
        self._msg_size = 100
        # 消息队列
        self._queue = None

    @property
    def time(self):
        return self._time

    @time.setter
    @typecheck(int)
    def set_time(self, time):
        if time > 0:
            self._time = time
        else:
            raise ValueError('time must bigger than 0')

    @property
    def routing_key(self):
        return self._routing_key

    @routing_key.setter
    @typecheck(str)
    def set_routing_key(self, routing_key):
        if len(routing_key) > 0:
            self._routing_key = routing_key
        else:
            raise ValueError('routing_key cannot be an empty string')

    @property
    def exchange(self):
        return self._exchange

    @exchange.setter
    @typecheck(str)
    def set_exchange(self, exchange):
        if len(exchange) > 0:
            self._exchange = exchange
        else:
            raise ValueError('exchange cannot be an empty string')

    @property
    def auto_ack(self):
        return self._auto_ack

    @auto_ack.setter
    @typecheck(bool)
    def set_auto_ack(self, auto_ack):
        self._auto_ack = auto_ack

    @property
    def multi_ack(self):
        return self._multi_ack

    @multi_ack.setter
    @typecheck(int)
    def set_multi_ack(self, multi_ack):
        if multi_ack > 0:
            self._multi_ack = multi_ack
        else:
            raise ValueError('multi_ack must at least 1')

    @property
    def persistent(self):
        return self._persistent

    @persistent.setter
    @typecheck(bool)
    def set_persistent(self, persistent):
        self._persistent = persistent

    @property
    def prefetch(self):
        return self._prefetch

    @prefetch.setter
    @typecheck(int)
    def set_prefetch(self, prefetch):
        if prefetch >= 0:
            self._prefetch = prefetch
        else:
            raise ValueError('prefetch cannot be negative')

    @property
    def productor_rate(self):
        return self._productor_rate

    @productor_rate.setter
    @typecheck(int, list)
    def set_productor_rate(self, productor_rate):
        if isinstance(productor_rate, int) and productor_rate <= 0:
            raise ValueError('productor rate must bigger than 0')
        self._productor_rate = productor_rate

    @property
    def consumer_rate(self):
        return self._consumer_rate

    @consumer_rate.setter
    @typecheck(int)
    def set_consumer_rate(self, consumer_rate):
        if consumer_rate <= 0:
            raise ValueError('consumer rate must bigger than 0')
        self._consumer_rate = consumer_rate

    @property
    def msg_properties(self):
        return self._msg_properties

    @msg_properties.setter
    @typecheck(dict)
    def set_msg_properties(self, msg_properties):
        self._msg_properties = msg_properties

    @property
    def role(self):
        return self._role

    @role.setter
    @typecheck(str)
    def set_role(self, role):
        '''
        设置任务角色, 只作为生产者或消费者, 或者二者兼有
        :param role: productor, consumer, all
        :return:
        '''
        if role in ['productor', 'consumer', 'all']:
            self._role = role
        else:
            raise ValueError('Role must be in "productor" "consumer" "all"')

    @property
    def msg_size(self):
        return self._msg_size

    @msg_size.setter
    @typecheck(int, list)
    def set_msg_size(self, msg_size):
        if isinstance(msg_size, int) and msg_size <= 0:
            raise ValueError('msg size must bigger than 0')
        self._msg_size = msg_size

    @property
    def queue(self):
        return self._queue

    @queue.setter
    @typecheck(FixedQueue, DynamicQueue)
    def set_queue(self, queue):
        self._queue = queue