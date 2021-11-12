'''
@author : johnwest
@github : https://github.com/JohnWes7/Daily_Nutrition
从GitHub检擦代码更新
如有更新直接下载覆盖
'''
# 模块检测
from src import tool
if __name__ == '__main__':
    tool.check_module()
from bs4 import BeautifulSoup
from urllib import request
from git.repo import Repo
import os
from config import config
from config import path
import downloads

class gitpy:
    def __init__(self,name:str,) -> None:
        self.name = name
        self.href
        pass


def cover_update_with_git():
    '''
    如果文件夹中有git文件可以直接用该方法从github上面克隆覆盖本地仓库\n
    但因为直接下载zip没有git 所以暂且缓一缓
    '''
    try:
        repo = Repo(os.path.dirname(__file__))
        repo.remote().pull()
    except Exception as e:
        print('发生异常: ', e, '\n尝试强制覆盖')
        try:
            g = repo.git
            g.fetch('--all')
            g.reset('--hard', 'main')
            g.pull()
        except Exception as e:
            print('强制git发生异常', e)
    finally:
        repo.close()


def test_git_pull():
    while True:
        ans = input('是否进行github强制覆盖更新(Y/n)')
        if ans.__eq__('Y'):
            cover_update_with_git()
            break
        elif ans.__eq__('n'):
            break
        else:
            print('输入错误')
            continue


def ispy(name: str):
    temp = os.path.splitext(name)
    if temp[len(temp)-1].__eq__('.py'):
        return True
    return False


def get_all_githubrepo_py(url: str):
    '''
    返回GitHub仓库中所有的.py文件的字典列表\n
    如果获取失败则返回false
    '''
    # 连接github页面
    i = 0
    while i < config.get_retry():
        try:
            print(f'尝试次数{i} 正在连接{url}')
            resp = request.urlopen(url)
            print(f'response: {resp.getcode()}')
            break
        except Exception as e:
            i += 1
            print('发生错误', e)
            if i == config.get_retry():
                print('请检擦网络连接 代理连接')
                return False

    html = resp.read().decode()

    # 拿到所有仓库所展示的项目
    soup = BeautifulSoup(html, 'html.parser')
    files = soup.select('div[aria-labelledby="files"] div[role="rowheader"] a')

    # print(files)
    per = 'https://github.com'

    filelist = []
    for file in files:
        href = file.attrs.get('href')
        name = file.attrs.get('title')
        fileurl = per + href

        if name.__eq__('Go to parent directory'):
            continue

        elif href.find('tree') >= 0:
            print(f'遍历到文件夹 {name}')
            # 遍历子文件夹
            temp = get_all_githubrepo_py(fileurl)
            # 如果子文件夹失败获取失败直接结束程序返回false
            if type(temp) == list:
                filelist.extend(temp)
            else:
                return False

        elif ispy(name):
            # https://raw.githubusercontent.com/JohnWes7/Daily_Nutrition/main/config.py
            # https://github.com/JohnWes7/Daily_Nutrition/blob/main/src/__init__.py
            print(f'遍历到py文件 {name}')
            filedict = {}
            filedict['name'] = name
            filedict['href'] = href
            relative = href.split('main/')  # 文件相对路径
            relative = relative[len(relative)-1]
            filedict['relative'] = relative
            filedict['temppath'] = None
            filelist.append(filedict)

    return filelist


def downloadpy(pylist: list[dict], dir:str = path.get_data_temp_dir()):
    '''
    传入要下载的 pylist列表 和 暂存文件夹
    下载全部list里面的py文件
    返回装有成功和失败的list
    其中的每一项包含了所有的
    '''
    faillist = []
    successlist = []
    per = 'https://raw.githubusercontent.com'
    for item in pylist:
        name = item.get('name')
        href = item.get('href').replace('/blob/', '/')
        url = per + href

        resp = None
        i = 0
        while i < config.get_retry():
            try:
                print(f'第{i}次尝试下载 正在下载 {name} : {url}')
                resp = request.urlopen(url)
                print(f'response: {resp.getcode()}')

                # 读取代码并保存
                code = resp.read().decode()

                # 如果文件夹不存在创建
                # path : /JohnWes7/Daily_Nutrition/main/src/__init__.py
                filepath = dir + item.get('relative')
                dirpath = os.path.dirname(filepath)  # 文件夹路径

                if not os.path.exists(dirpath):
                    os.makedirs(dirpath)

                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(code)
                temp = item.copy()
                temp['temppath'] = filepath
                successlist.append(temp)

                break
            except Exception as e:
                i += 1
                print(e)
                if i == config.get_retry():
                    print(f'{name}下载失败')
                    faillist.append(item.copy())

    result = {
        'successlist': successlist,
        'faillist': faillist
    }
    return result


def replacepy():
    pass


def tips(filelist: list[dict]):
    print('='*30, 'info', '='*30)
    print(f'找到{len(filelist)}个文件')
    for item in filelist:
        print(item.get('name'))
    print('='*60)


if __name__ == '__main__':

    opener = downloads.build_custom_opener()
    request.install_opener(opener=opener)

    # 连接部分
    filelist = None
    print('='*30, '开始获取仓库信息', '='*30)
    while True:
        # 遍历获得仓库所有py文件信息
        github_url = 'https://github.com/JohnWes7/Daily_Nutrition'
        filelist = get_all_githubrepo_py(github_url)

        if type(filelist) == list:
            break
        # 如果获取不到 返回false 重新获取
        else:
            input('获取仓库信息失败 回车重新尝试连接下载github\n')
            continue
    print('='*30, '仓库信息获取完毕', '='*30, end='\n\n')

    # 打印提示
    tips(filelist)
    input('按下回车开始下载')

    #下载部分
    print('='*30, '开始下载', '='*30)
    downloadlist = filelist
    templ = []
    while True:
        # 下载
        result = downloadpy(downloadlist)
        # 成功跳出
        fail = result.get('faillist')
        succ = result.get('successlist')
        templ.extend(succ)
        if len(fail) == 0:
            break
        # 失败重新尝试
        else:
            print(f'{len(fail)}个下载失败：')
            for item in fail:
                print(item.get('name'), end=' ')
            print()
            input('按下回车重新尝试下载失败项')
            downloadlist = fail

    #覆盖部分
    cwd = path.getcwd()
    for item in templ:
        temp = open(item.get('temppath'),'r',encoding='utf-8')
        temp_data = temp.read()
        local = open(cwd+item.get('relative'),'w',encoding='utf-8')
        local.write(temp_data)

        temp.close()
        local.close()
        os.remove(item.get('temppath'))
    
    input('done')
