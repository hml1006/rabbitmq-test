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

    def print(self):
        print('server: ')
        print('\tip: %s' % self.server_ip)
        print('\tport: %s' % self.server_port)

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

        server = yaml_data['server']
        if not isinstance(server, dict):
            raise ValueError('server config type error')

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

        Config.__config = config