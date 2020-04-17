'''
启动http服务, 提供restfull风格api
'''
import tornado.ioloop
import tornado.httpserver
import pyrestful.rest
import argparse
import sys
from config.config import Config
from api.task import TaskService
from api.crash import CrashService
from api.resource import NodeService, RmqStatService, MachineStatService
from orm.database import Database

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str, dest='file', help='Server yaml config file path')
    args = parser.parse_args()
    # 配置文件路径
    if not args.file:
        print('Yaml config file should be set')
        parser.print_help()
        sys.exit(-1)

    # 初始化配置
    Config.init(args.file)
    cfg = Config.get_instance()
    cfg.print()


    db_instance = Database.get_instance()
    # 监听
    app = pyrestful.rest.RestService([TaskService, CrashService, \
                                      NodeService, RmqStatService, MachineStatService], dict(database = db_instance))
    app.listen(address=cfg.server_ip, port=cfg.server_port)
    # 事件循环
    tornado.ioloop.IOLoop.instance().start()