'''
html/js/css/图片请求
'''

import pyrestful.rest
from pyrestful import mediatypes
from pyrestful.rest import get, post, delete
from error.error import Error
from orm.database import Task as OrmTask, TaskSeq

class TaskService(pyrestful.rest.RestHandler):
    def initialize(self, database):
        self.database = database

    @get(_path='/')
    def home(self):
        pass

