import yaml

def parse_yaml(path):
    '''
    解析yaml配置
    :param path:
    :return:
    '''
    # 打开读取yaml文件
    file = open(path, 'r', encoding='utf8')
    file_data = file.read()

    # 解析yaml数据
    yaml_data = yaml.load(file_data)
    return yaml_data