'''
服务器配置, 数据库配置
'''
import yaml
from utils.typecheck import typecheck

class Config:
    def __init__(self):
        pass

    @property
    def server_ip(self):
        return self.__server_ip

    @server_ip.setter
    @typecheck(str)
    def server_ip(self, server_ip):
        self.__server_ip = server_ip

    @property
    def server_port(self):
        return self.__server_port

    @server_port.setter
    @typecheck(int)
    def server_port(self, server_port):
        if server_port > 0 and server_port < 65536:
            self.__server_port = server_port
        else:
            raise ValueError('Wrong server port: %d' % server_port)

    @property
    def db_host(self):
        return self.__db_ip

    @db_host.setter
    @typecheck(str)
    def db_host(self, db_ip):
        self.__db_ip = db_ip

    @property
    def db_port(self):
        return self.__db_port

    @db_port.setter
    @typecheck(int)
    def db_port(self, db_port):
        if db_port > 0 and db_port < 65536:
            self.__db_port = db_port
        else:
            raise ValueError('Wrong database port: %d' % db_port)

    @property
    def db_name(self):
        return self.__db_name

    @db_name.setter
    @typecheck(str)
    def db_name(self, db_name):
        self.__db_name = db_name

    @property
    def db_user(self):
        return self.__db_user

    @db_user.setter
    @typecheck(str)
    def db_user(self, db_user):
        self.__db_user = db_user

    @property
    def db_password(self):
        return self.__db_password

    @db_password.setter
    @typecheck(str)
    def db_password(self, db_password):
        self.__db_password = db_password

    def print(self):
        print('server: ')
        print('\tip: %s' % self.server_ip)
        print('\tport: %s' % self.server_port)
        print('database: ')
        print('\tip: %s' % self.db_host)
        print('\tport: %s' % self.db_port)
        print('\tname: %s' % self.db_name)
        print('\tuser: %s' % self.db_user)
        print('\tpassword: %s' % self.db_password)

    # 全局配置
    __config = None

    @classmethod
    def get_instance(cls):
        if not Config.__config:
            raise ValueError('config not init')
        return Config.__config

    @classmethod
    def init(cls, path):
        if not path or len(path) == 0:
            raise ValueError('Yaml path error: %s' % path)

        file = open(path, 'r', encoding='utf8')
        file_data = file.read()
        file.close()

        # 解析yaml数据
        yaml_data = yaml.load(file_data)
        if not isinstance(yaml_data, dict):
            raise ValueError('Wrong config type')
        if 'server' not in yaml_data:
            raise ValueError('server config not found in yaml')
        if 'database' not in yaml_data:
            raise ValueError('database config not found in yaml')
        server = yaml_data['server']
        database = yaml_data['database']
        if not isinstance(server, dict):
            raise ValueError('server config type error')
        if not isinstance(database, dict):
            raise ValueError('data config type error')

        config = Config()
        if 'ip' not in server:
            # 如果未设置要监听的网卡地址, 设置默认值
            config.server_ip = '0.0.0.0'
        else:
            config.server_ip = server['ip']

        if 'port' not in server:
            raise ValueError('server port must be set')
        else:
            config.server_port = server['port']

        if 'host' not in database:
            raise ValueError('database host must be set')
        else:
            config.db_host = database['host']

        if 'port' not in database:
            # 设置默认数据库端口
            config.db_port = 3306
        else:
            config.db_port = database['port']

        if 'name' not in database:
            # 设置默认数据库名称
            config.db_name = 'rmqtest'
        else:
            config.db_name = database['name']

        if 'user' not in database:
            raise ValueError('database username must be set')
        else:
            config.db_user = database['user']

        if 'password' not in database:
            raise ValueError('database password not set')
        else:
            config.db_password = database['password']

        Config.__config = config