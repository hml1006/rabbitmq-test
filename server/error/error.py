'''
错误信息
'''
class Error:
    def __init__(self):
        pass

    @classmethod
    def success(cls):
        return 'success'

    @classmethod
    def params_fields_not_found(cls):
        return 'some fields required in json, please check it'

    @classmethod
    def task_exists(cls):
        return 'task has been exist'

    @classmethod
    def task_not_exists(cls):
        return 'task not exists'

    @classmethod
    def unknown_error(cls):
        return 'unknown error'

    @classmethod
    def data_not_in_db(cls):
        return 'query results is empty'