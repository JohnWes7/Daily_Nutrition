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
from bs4 import BeautifulSoup

module_dict = {
    'lxml' : 'lxml',
    'selenium' : 'selenium',
    'git':'gitpython'
}

github_api_url ='https://api.github.com/repos/JohnWes7/Daily_Nutrition'
github_page_url = 'https://github.com/JohnWes7/Daily_Nutrition' 


def check_module(module_dict:dict=module_dict):
    print('开始检测')
    for key,value in module_dict.items():
        i = 0
        while i < config.get_retry():
            try:
                __import__(key)
                print(f'导入{key}模块成功')
                break
            except Exception as e:

                print(f'导入{key}模组失败,尝试进行安装 尝试次数:{i}')
                command = f'pip install -i https://pypi.tuna.tsinghua.edu.cn/simple {value}'
                with os.popen(command,'r') as p:
                    print(e)
                    r = p.read()
                    if r.find(f'Successfully installed {value}') or r.find('Requirement already satisfied'):
                        print('安装成功')
                        break
                    else:
                        continue