import yaml

class Config:
    def __init__(self):
        pass

    @property
    def node_id(self):
        return self.__node_id

    @node_id.setter
    def node_id(self, node_id):
        self.__node_id = node_id

    @property
    def rmq_host(self):
        return self.__rmq_host

    @rmq_host.setter
    def rmq_host(self, host):
        self.__rmq_host = host

    @property
    def rmq_port(self):
        return self.__rmq_port

    @rmq_port.setter
    def rmq_port(self, port):
        self.__rmq_port = port

    @property
    def rmq_user(self):
        return self.__rmq_user

    @rmq_user.setter
    def rmq_user(self, username):
        self.__rmq_user = username

    @property
    def rmq_password(self):
        return self.__rmq_password

    @rmq_password.setter
    def rmq_password(self, password):
        self.__rmq_password = password

    @property
    def collect_host(self):
        return self.__collect_host

    @collect_host.setter
    def collect_host(self, host):
        self.__collect_host = host

    @property
    def collect_port(self):
        return self.__collect_port

    @collect_port.setter
    def collect_port(self, port):
        self.__collect_port = port

    instance = None

    @classmethod
    def init(cls, path):
        f = open(path, 'r')
        config = yaml.load(f)
        f.close()

        Config.instance = Config()
        rmq = config['rabbitmq']
        Config.instance.rmq_host = rmq['host']
        Config.instance.rmq_port = rmq['manage_port']
        Config.instance.rmq_user = rmq['username']
        Config.instance.rmq_password = rmq['password']

        collect = config['collect']
        Config.instance.collect_host = collect['host']
        Config.instance.collect_port = collect['port']

    @classmethod
    def get_instance(cls):
        if Config.instance == None:
            raise Exception('config not initlized')
        return Config.instance