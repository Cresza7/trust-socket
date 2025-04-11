"""
读取TRUST ID程序
题目要求不使用额外的Python包，但对于环境变量的读取一般要用到os包中的接口
因此程序设计了两个方法读取TRUST ID，封装为不同的函数：
1. 使用文件"模拟"环境变量，则可以不引入额外包
2. 使用os中的接口获取真正环境变量
在程序中，设置为先从环境变量读取TRUST ID，没有就用文件中的，再没有就用默认值(get_trust_id()函数)
优先级：环境变量 > 文件 > 默认值
"""


# 1. 使用文件"模拟"环境变量，不引入额外包
# 按需设置默认TRUST ID
# 假设TRUST ID位于trust_id.txt文件中
def read_file_id(filename='trust_id.txt', default_server_id='1111'):
    """
    从本地文件读取 TRUST ID，失败则返回默认值
    :param filename: 本地文件名
    :param default_server_id: 默认TRUST ID
    :return: TRUST ID
    """
    try:
        with open(filename, 'r') as f:
            # 读取TRUST ID
            content = f.read().strip()
            # 空值检查
            if not content:
                raise ValueError("文件内容为空")
            # 返回读取到的TRUST ID
            return content
    except (FileNotFoundError, PermissionError) as e:
        print(f'文件读取失败：{e}，使用默认TRUST ID！')
        # 返回默认值
        return default_server_id
    except Exception as e:
        print(f'未知文件错误：{e}')
        # 返回默认值
        return default_server_id


# 2. 使用os中的接口获取真正环境变量(按需设置默认TRUST ID)
def read_environ_id(default_server_id='1111'):
    """
    从系统环境变量中读取 TRUST ID，失败则返回默认值
    :param default_server_id: 默认TRUST ID
    :return: TRUST ID
    """
    import os
    # 从环境变量中读取TRUST ID，若无则为默认id
    trust_id = os.environ.get('TRUST_ID', default_server_id)
    return trust_id


def get_trust_id(filename='trust_id.txt'):
    """
    先从环境变量读取TRUST ID，没有就用文件中的，再没有就用默认值
    优先级：环境变量 > 文件 > 默认值
    :return: TRUST ID
    """
    # 先从环境变量读取TRUST ID
    trust_id = read_environ_id(default_server_id=None)
    if trust_id:
        # 读取到则返回
        return trust_id
    # 未读取到，则继续从文件中读取
    return read_file_id(filename=filename)
