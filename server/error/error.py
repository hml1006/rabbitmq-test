'''
错误信息
'''
class Error(Enum):
    def __init__(self):
        pass

    @classmethod
    def success(cls):
        return 'success'

    @classmethod
    def json_fields_not_found(cls):
        return 'some fields required in json, please check it'

    @classmethod
    def task_exists(cls):
        return 'task has been exist'

    @classmethod
    def task_not_exists(cls):
        return 'task not exists'