
def typecheck(*types):
    '''
    属性检查
    :param prop_type:
    :param kargchecks:
    :return:
    '''
    def on_decorator(func):
        def on_call(*args, **kargs):
            ret = False
            for prop_type in types:
                if isinstance(args[1], prop_type):
                    ret = True
            if not ret:
                raise TypeError('Value type error, must in %s' % (str(types)))
            return func(*args, **kargs)
        return on_call
    return on_decorator
