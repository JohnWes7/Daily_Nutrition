'''
@author : johnwest
@github : https://github.com/JohnWes7/Daily_Nutrition
工具命名空间
'''
import os
import sys
from urllib import request
dirpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,dirpath)
from config import config
import json

module_dict = {
    'selenium' : 'selenium',
}


def check_module(module_dict:dict=module_dict):
    print('开始检测模组')
    for key,value in module_dict.items():
        i = 0
        while i < config.get_retry():
            try:
                __import__(key)
                print(f'导入{key}模块成功')
                break
            except Exception as e:
                i+=1
                print(f'导入{key}模组失败,尝试进行安装 尝试次数:{i}')
                command = f'pip install -i https://pypi.tuna.tsinghua.edu.cn/simple {value}'
                with os.popen(command,'r') as p:
                    print(e)
                    r = p.read()
                    if r.find(f'Successfully installed {value}') or r.find('Requirement already satisfied'):
                        print('安装成功')
                        break
                    else:
                        if i == config.get_retry():
                            return False
                        continue
    return True

def check():
    judge = check_module()
    if not judge:
        input('模组检测失败，请手动下载或者检查网络环境重新执行程序')
        sys.exit(1)

def get_json_data(path: str):
    '''
    获得json数据
    从path中按照utf-8编码读取数据
    并且自动转成json格式
    '''
    data = None
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as file:
            data = json.loads(file.read())

    return data

def save_str_data(path: str, json_str: str):
    '''
    存储str数据到path路径
    '''
    with open(path, 'w', encoding='utf-8') as file:
        file.write(json_str)