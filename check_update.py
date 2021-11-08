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
    cover_update()
    