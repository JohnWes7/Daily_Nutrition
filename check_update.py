'''
@author : johnwest
@github : https://github.com/JohnWes7/Daily_Nutrition
从GitHub检擦代码更新
如有更新直接下载覆盖
'''
#模块检测
from src import tool
if __name__=='__main__':
    tool.check_module()
from bs4 import BeautifulSoup
from urllib import request
from git.repo import Repo
import os
from config import config
import downloads


def cover_update_with_git():
    '''
    如果文件夹中有git文件可以直接用该方法从github上面克隆覆盖本地仓库\n
    但因为直接下载zip没有git 所以暂且缓一缓
    '''
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


def ispy(name:str):
    temp = os.path.splitext(name)
    if temp[len(temp)-1].__eq__('.py'):
        return True
    return False


def get_all_githubrepo_py(url:str):
    '''
    返回GitHub仓库中所有的.py文件的字典列表\n
    如果获取失败则返回false
    '''
    #连接github页面
    i = 0
    while i<config.get_retry():
        try:
            print(f'尝试次数{i} 正在连接{url}')
            resp = request.urlopen(url)
            print(f'response: {resp.getcode()}')
            break
        except Exception as e:
            i+=1
            print('发生错误',e)
            if i == config.get_retry():
                print('请检擦网络连接 代理连接')
                return False

    html = resp.read().decode()

    #拿到所有仓库所展示的项目
    soup = BeautifulSoup(html,'html.parser')
    files = soup.select('div[aria-labelledby="files"] div[role="rowheader"] a')
    
    # print(files)
    per = 'https://github.com'

    filelist = []
    for file in files:
        path = file.attrs.get('href')
        name = file.attrs.get('title')
        href = per + path

        if name.__eq__('Go to parent directory'):
            continue

        elif path.find('tree') >= 0:
            print(f'遍历到文件夹 {name}')
            #遍历子文件夹
            temp = get_all_githubrepo_py(href)
            #如果子文件夹失败获取失败直接结束程序返回false
            if type(temp) == list:
                filelist.extend(temp)
            else:
                return False

        elif ispy(name):
            #https://raw.githubusercontent.com/JohnWes7/Daily_Nutrition/main/config.py
            #https://github.com/JohnWes7/Daily_Nutrition/blob/main/src/__init__.py
            print(f'遍历到py文件 {name}')
            filedict = {}
            filedict['name'] = name
            filedict['path'] = path
            filedict['temppath'] = None
            filelist.append(filedict)

    return filelist


def downloadpy(pylist:list[dict]):
    '''
    下载全部list里面的py文件
    '''
    faillist = []
    per = 'https://raw.githubusercontent.com'
    temppath = config.data_temp_dir
    for item in pylist:
        name = item.get('name')
        path = item.get('path').replace('/blob/','/')
        url = per + path

        resp = None
        i = 0
        while i < config.get_retry():
            try:
                print(f'第{i}次尝试下载 正在下载 {name} : {url}')
                resp = request.urlopen(url)
                print(f'response: {resp.getcode()}')

                #读取代码并保存
                code = resp.read().decode()
                #如果temp文件夹不存在创建
                if not os.path.exists(temppath):
                    os.makedirs(temppath)

                with open(temppath+name,'w',encoding='utf-8') as file:
                    item['temppath'] = temppath+name
                    file.write(code)
                
                break
            except Exception as e:
                i+=1
                print(f'response: {resp.getcode()}\n',e)
                if i == config.get_retry():
                    print(f'{name}下载失败')
                    faillist.append(item)
    return faillist


def replacepy():
    pass
                    
                
def tips(filelist:list[dict]):
    print('='*30,'info','='*30)
    print(f'找到{len(filelist)}个文件')
    for item in filelist:
        print(item.get('name'))
    print('='*60)


if __name__ == '__main__':
    
    opener = downloads.build_custom_opener()
    request.install_opener(opener=opener)

    #连接
    filelist = None
    print('='*30,'开始获取仓库信息','='*30)
    while True:
        #遍历获得仓库所有py文件信息
        github_url = 'https://github.com/JohnWes7/Daily_Nutrition'
        filelist = get_all_githubrepo_py(github_url)
        
        if type(filelist) == list:
            break
        #如果获取不到 返回false 重新获取
        else:
            input('获取仓库信息失败 回车重新尝试连接下载github\n')
            continue
    print('='*30,'仓库信息获取完毕','='*30,end='\n\n')

    #打印提示
    tips(filelist)
    input('按下回车开始下载')

    print('='*30,'开始下载','='*30)
    while True:
        #下载
        fail = downloadpy(filelist)
        #成功跳出
        if len(fail) == 0:
            break
        #失败重新尝试
        else:
            print(f'{len(fail)}个下载失败：')
            for item in fail:
                print(item.get('name'),end=' ')
            print()
            input('按下回车重新尝试下载失败项')