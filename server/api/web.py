'''
html/js/css/图片请求
'''
import os
import pyrestful.rest
from pyrestful import mediatypes
from pyrestful.rest import get, post, delete
from error.error import Error
from orm.database import Task as OrmTask, TaskSeq

class WebService(pyrestful.rest.RestHandler):
    def initialize(self, database):
        self.database = database

    @get(_path='/')
    def home(self):
        script_path = os.path.abspath(__file__)
        script_dir = os.path.dirname(script_path)
        html_path = os.path.abspath(script_dir + '/../web/index.html')
        file = open(html_path, 'r')
        content = file.read()
        file.close()
        self.set_header('Content-Type', 'text/html')
        return content

    @get(_path='/jquery-3.5.0.min.js')
    def jquery(self):
        script_path = os.path.abspath(__file__)
        script_dir = os.path.dirname(script_path)
        html_path = os.path.abspath(script_dir + '/../web/jquery-3.5.0.min.js')
        file = open(html_path, 'r')
        content = file.read()
        file.close()
        self.set_header('Content-Type', 'application/javascript')
        return content

    @get(_path='/echarts.min.js')
    def echarts(self):
        script_path = os.path.abspath(__file__)
        script_dir = os.path.dirname(script_path)
        html_path = os.path.abspath(script_dir + '/../web/echarts.min.js')
        file = open(html_path, 'r')
        content = file.read()
        file.close()
        self.set_header('Content-Type', 'application/javascript')
        return content

