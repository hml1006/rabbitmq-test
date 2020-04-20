import os

def get_file_size(file):
    '''
    获取文件或目录空间大小
    :param file:
    :return:
    '''
    # 判断是否存在
    if not os.path.exists(file):
        print(file, '文件不存在，无法统计')
        return None
    # 是普通文件
    if os.path.isfile(file):
        return os.path.getsize(file)
    # 是目录，递归统计里面的文件，最终得出目录的大小
    total = 0
    dirs = os.listdir(file)
    for f in dirs:
        file_name = os.path.join(file, f)
        if os.path.isfile(file_name):
            total += os.path.getsize(file_name)
        else:
            total += get_file_size(file_name)

def get_dist_free(path):
    '''
    获取文件所在分区的剩余空间大小
    :param path:
    :return:
    '''
    if path == None:
        return 0
    if not os.path.exists(path):
        return 0
    stat = os.statvfs(path)
    return stat.f_bsize * stat.f_bfree