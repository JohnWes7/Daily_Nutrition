'''
@author : johnwest
@github : https://github.com/JohnWes7/Daily_Nutrition
从GitHub检擦代码更新
如有更新直接下载覆盖
'''
# 模块检测
from src import tool
if __name__ == '__main__':
    tool.check()
from bs4 import BeautifulSoup
from urllib import request
import os
from config import config
from config import path
import downloads


class py_info:
    def __init__(self, name: str, href: str) -> None:
        self.name = name
        self.href = href
        self.__temppath = None

    def get_relative(self):
        '''
        获得文件相对路径
        '''
        relative = self.href.split('main/')
        relative = relative[len(relative)-1]
        return relative

    def get_raw_url(self):
        '''获得raw界面的网址'''
        return 'https://raw.githubusercontent.com'+self.href.replace('/blob/', '/')

    def get_temppath(self):
        return self.__temppath

    @staticmethod
    def __progressbar(chunk: int, chunk_num: int, total: int):
        '''进度条'''
        barmaxcount = 20 #进度条格子数量
        if total == 0:
            per = 1
        else:
            per = 1.0 * chunk * chunk_num / total
        if per > 1:
            per = 1
        kb = total/1024
        count = int(barmaxcount*per)

        print('\rdownload {0:.2f}% :|{1}{2}| total:{3:.2f}KB'.format(
            per*100, '■'*count, ' '*(barmaxcount-count), kb),end='')

    def download(self, rootdir: str = path.get_data_temp_dir()):
        '''下载该pyinfo的数据到指定目录 返回下载是否成功'''
        url = self.get_raw_url()

        resp = None
        i = 0
        while i < config.get_retry():
            try:
                # 如果文件夹不存在创建
                # path : /JohnWes7/Daily_Nutrition/main/src/__init__.py
                filepath = rootdir + self.get_relative()
                dirpath = os.path.dirname(filepath)  # 文件夹路径

                if not os.path.exists(dirpath):
                    os.makedirs(dirpath)

                print(f'第{i}次尝试下载 正在下载 {self.name} : {url}')
                request.urlretrieve(url=url, filename=filepath,
                                    reporthook=py_info.__progressbar)
                print()
                # resp = request.urlopen(url)
                # print(f'response: {resp.getcode()}')

                # # 读取代码并保存
                # code = resp.read().decode()
                # with open(filepath, 'w', encoding='utf-8') as file:
                #     file.write(code)
                self.__temppath = filepath

                break
            except Exception as e:
                i += 1
                print(e)
                if i == config.get_retry():
                    print(f'{self.name}下载失败')
                    return False

        return True


def ispy(name: str):
    temp = os.path.splitext(name)
    if temp[len(temp)-1].__eq__('.py'):
        return True
    return False


def get_all_githubrepo_py(url: str) -> list[py_info]:
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
            info = py_info(name=name, href=href)
            filelist.append(info)

    return filelist


def downloadpy(pylist: list[py_info], dir: str = path.get_data_temp_dir()) -> list[py_info]:
    '''
    传入要下载的 pylist列表 和 暂存文件夹
    下载全部list里面的py文件
    返回下载失败的项目list
    '''
    faillist = []

    for pyinfo in pylist:
        if not pyinfo.download(rootdir=dir):
            faillist.append(pyinfo)

    return faillist


def replacepy():
    pass


def tips(filelist: list[py_info]):
    print('='*30, 'info', '='*30)
    print(f'找到{len(filelist)}个文件')
    for item in filelist:
        print(item.name)
    print('='*60)


def main():
    # 单独设置代理
    ans = input('是否按照Config.ini 设置代理? Y/n\n')
    if ans.__eq__('Y'):
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

    # 下载部分
    print('='*30, '开始下载', '='*30)
    downloadlist = filelist
    while True:
        # 下载
        fail = downloadpy(downloadlist)
        # 成功跳出
        if len(fail) == 0:
            break
        # 有失败项目重新尝试
        else:
            print(f'{len(fail)}个下载失败：')
            for info in fail:
                print(info.name, end=' ')
            print()
            input('按下回车重新尝试下载失败项')
            downloadlist = fail
    print('='*30, '下载完成', '='*30, end='\n\n')

    # 覆盖部分
    print('='*30, '开始覆盖', '='*30)
    replacelist = filelist
    cwd = path.getcwd()

    while True:
        failr = []
        for info in replacelist:
            try:
                name = info.name
                print(f'正在写入{name}')
                # 打开下载的文件
                temp = open(info.get_temppath(), 'r', encoding='utf-8')
                temp_data = temp.read()
                # 打开本地需要替换或者新建的位置
                local = open(cwd+info.get_relative(), 'w', encoding='utf-8')
                local.write(temp_data)

                temp.close()
                local.close()
                os.remove(info.get_temppath())
                print('写入成功')
            except Exception as e:
                failr.append(info)
                print('错误', e)

        if len(failr) == 0:
            print('全部写入成功')
            break
        else:
            print(f'{len(failr)}个写入失败尝试重试')
            for info in failr:
                print(info.name, end='')
            print()
            replacelist = failr
    print()

    input('done')


if __name__ == '__main__':
    main()

    # opener = downloads.build_custom_opener()
    # resp = opener.open(
    #     'https://raw.githubusercontent.com/JohnWes7/Daily_Nutrition/main/discovery.py')
    # print(type(resp))
    # print(resp.getheaders())
    # print(resp.read().decode())


# def cover_update_with_git():
#     '''
#     如果文件夹中有git文件可以直接用该方法从github上面克隆覆盖本地仓库\n
#     但因为直接下载zip没有git 所以暂且缓一缓
#     '''
#     try:
#         repo = Repo(os.path.dirname(__file__))
#         repo.remote().pull()
#     except Exception as e:
#         print('发生异常: ', e, '\n尝试强制覆盖')
#         try:
#             g = repo.git
#             g.fetch('--all')
#             g.reset('--hard', 'main')
#             g.pull()
#         except Exception as e:
#             print('强制git发生异常', e)
#     finally:
#         repo.close()


# def test_git_pull():
#     while True:
#         ans = input('是否进行github强制覆盖更新(Y/n)')
#         if ans.__eq__('Y'):
#             cover_update_with_git()
#             break
#         elif ans.__eq__('n'):
#             break
#         else:
#             print('输入错误')
#             continue
