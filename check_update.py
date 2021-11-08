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
    repo = Repo(os.path.dirname(__file__))
    g = repo.git
    g.fetch('--all')
    g.reset('--hard','main')
    g.pull()


if __name__ == '__main__':
    while True:
        ans = input('是否进行github强制覆盖更新(Y/n)')
        if ans.__eq__('Y'):
            cover_update()
        elif ans.__eq__('n'):
            break
        else:
            continue
    