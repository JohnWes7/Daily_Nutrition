'''
@author : johnwest
@github : https://github.com/JohnWes7/Daily_Nutrition
'''
from src import tool
if __name__=='__main__':
    tool.check_module()
from git.repo import Repo
import os


def cover_update():
    try:
        repo = Repo(os.path.dirname(__file__))
        repo.remote().pull()
    except Exception as e:
        print('发生异常: ',e,'\n尝试强制覆盖')
        try:
            g = repo.git
            g.fetch('--all')
            g.reset('--hard','main')
            g.pull()
        except Exception as e:
            print('强制git发生异常',e)
    finally:
        repo.close()


if __name__ == '__main__':
    while True:
        ans = input('是否进行github强制覆盖更新(Y/n)')
        if ans.__eq__('Y'):
            cover_update() 
            break
        elif ans.__eq__('n'):
            break
        else:
            print('输入错误')
            continue
    