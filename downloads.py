'''
@author : johnwest
@github : https://github.com/JohnWes7/Daily_Nutrition
'''


from posixpath import relpath
from src import tool
if __name__ == '__main__':
    tool.check()
from config import path, url, recordcookie, config
from types import FunctionType
from typing import Any
from urllib import request
from urllib.parse import (urlencode, _splittype)
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from bs4 import BeautifulSoup
import json
import os
import sys
from src import custom_driver
from urllib.error import ContentTooShortError
import tempfile
import contextlib


pixiv_discovery_api1 = 'https://www.pixiv.net/rpc/recommender.php?type=illust&sample_illusts=auto&num_recommendations=60&page=discovery&mode=all'
pixiv_discovery_api2 = 'https://www.pixiv.net/ajax/discovery/artworks'

_opener = None
_headtemplate = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.30',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
}


class illustration:

    def __init__(self, id) -> None:
        self.id = id  # id
        self.__name = None  # 文件名称
        self.__srclist = None  # 下载源

    def progressbar(block_num: int, block_size: int, total: int, name):
        '''进度条'''
        barmaxcount = 20  # 进度条格子数量
        if total == 0:
            per = 1
        else:
            per = 1.0 * block_num * block_size / total
        if per > 1:
            per = 1

        kb = total/1024
        size = '{0:.2f}KB'.format(kb)
        if kb > 1024:
            mb = kb/1024
            size = '{0:.2f}MB'.format(mb)

        count = int(barmaxcount*per)

        print('\rdownload {4} {0:.2f}% :|{1}{2}| total:{3}'.format(
            per*100, '■'*count, ' '*(barmaxcount-count), size, name), end='')

    def get_html(self, opener: request.OpenerDirector = None, headers=None) -> str:
        '''获得该插画主页html'''
        info_url = f'https://www.pixiv.net/artworks/{self.id}'
        global _opener
        if opener == None:
            print('默认opener')
            if _opener == None:
                opener = _opener = request.build_opener()
            else:
                opener = _opener
        if headers == None:
            headers = _headtemplate

        head = headers.copy()
        resp = opener.open(request.Request(
            url=info_url, headers=head, method='GET'))
        return resp.read().decode()

    def get_name(self, opener=None, headers=None):
        '''获取插画标题'''
        global _opener
        if self.__name == None:
            if opener == None:
                if _opener == None:
                    opener = _opener = request.build_opener()
                else:
                    opener = _opener
            if headers == None:
                headers = _headtemplate

            html = self.get_html(opener, headers)
            soup = BeautifulSoup(html, 'html.parser')
            tag = soup.select_one('meta[property="twitter:title"]')
            name = tag.attrs.get('content')

            name = name.replace('/', '')
            name = name.replace('\\', '')
            name = name.replace("'", '')
            name = name.replace('"', '')
            name = name.replace('?', '')
            name = name.replace('*', '')
            name = name.replace('<', '')
            name = name.replace('>', '')
            self.__name = name

        return self.__name

    def get_srclist(self, opener=None, headers=None) -> list:
        '''获取该插画的图源url'''
        global _opener
        if self.__srclist == None:
            if opener == None:
                if _opener == None:
                    opener = _opener = request.build_opener()
                else:
                    opener = _opener
            if headers == None:
                headers = _headtemplate

            src_url = f'https://www.pixiv.net/ajax/illust/{self.id}/pages?lang=zh'
            head = headers.copy()
            head['referer'] = f'https://www.pixiv.net/artworks/{self.id}'
            resp = opener.open(request.Request(
                src_url, headers=head, method='GET'))
            srcjson = resp.read().decode()
            srcjson = json.loads(srcjson)

            self.__srclist = srcjson.get('body')

        return self.__srclist

    def download(self, dir:str, opener=None, headers=None, image_quality: str = 'original', reporthook=progressbar):
        global _opener
        if opener == None:
            if _opener == None:
                opener = _opener = request.build_opener()
            else:
                opener = _opener
            if headers == None:
                headers = _headtemplate
        
        if not os.path.exists(dir):
            os.makedirs(dir)
        else:
            raise Exception('文件夹路径不存在')

        srclist = self.get_srclist(opener=opener, headers=headers)
        name = self.get_name(opener=opener, headers=headers)

        head = headers.copy()
        head['referer'] = 'https://www.pixiv.net/'
        for p, url in enumerate(srclist):
            imageurl = url.get('urls').get(image_quality)
            temp = os.path.splitext(imageurl)
            suffix = temp[len(temp) - 1]
            name = f'{self.id}_{name}_p{p}{suffix}'

            if dir[len(dir)-1] == '/' or dir[len(dir)-1] == '\\':
                filename = dir + name
            else:
                filename = dir + '/' + name
 
            filename = dir
            custom_urlretrieve(request.Request(imageurl, headers=head), opener=opener,
                               filename=filename, reporthook=lambda bn, bs, total: reporthook(bn,bs,total,f'{name} p{p}'))
            print()


def custom_urlretrieve(url, opener: request.OpenerDirector = None, filename=None, reporthook=None, data=None):
    """
    魔改urlretrieve 可以用opener
    Retrieve a URL into a temporary location on disk.

    Requires a URL argument. If a filename is passed, it is used as
    the temporary file location. The reporthook argument should be
    a callable that accepts a block number, a read size, and the
    total file size of the URL target. The data argument should be
    valid URL encoded data.

    If a filename is passed and the URL points to a local resource,
    the result is a copy from local file to new file.

    Returns a tuple containing the path to the newly created
    data file as well as the resulting HTTPMessage object.
    """
    if opener is None:
        opener = request.build_opener()

    u = url
    if type(url) == request.Request:
        u = url.full_url
    url_type, path = _splittype(u)

    with contextlib.closing(opener.open(url, data)) as fp:
        headers = fp.info()

        # Just return the local path and the "headers" for file://
        # URLs. No sense in performing a copy unless requested.
        if url_type == "file" and not filename:
            return os.path.normpath(path), headers

        # Handle temporary file setup.
        if filename:
            tfp = open(filename, 'wb')
        else:
            tfp = tempfile.NamedTemporaryFile(delete=False)
            filename = tfp.name

        with tfp:
            result = filename, headers
            bs = 1024*8
            size = -1
            read = 0
            blocknum = 0
            if "content-length" in headers:
                size = int(headers["Content-Length"])

            if reporthook:
                reporthook(blocknum, bs, size)

            while True:
                block = fp.read(bs)
                if not block:
                    break
                read += len(block)
                tfp.write(block)
                blocknum += 1
                if reporthook:
                    reporthook(blocknum, bs, size)

    if size >= 0 and read < size:
        raise ContentTooShortError(
            "retrieval incomplete: got only %i out of %i bytes"
            % (read, size), result)

    return result


def dicovery_json(head=None, opener=None):
    '''获取发现api数据'''
    # 检查传入opener
    if opener is None:
        opener = request.build_opener()
    if head == None:
        head = recordcookie.get_headtemplate()

    # 更改header
    head['referer'] = 'https://www.pixiv.net/discovery'

    # 获得查询字符串
    qd = config.get_discovery_query_dict()
    query_string = urlencode(qd)

    # request
    url = pixiv_discovery_api2 + '?' + query_string
    print(url)
    requ = request.Request(url, headers=head, method='GET')
    # open
    resp = opener.open(requ)
    print('pixiv: ', resp.getcode())
    r_bt = resp.read()
    r_str = r_bt.decode()
    resp_json = json.loads(r_str)

    return resp_json


def download_idlist(id_list: list[str], dir, opener=None, head=None, callback_delegate: FunctionType = None, retry=3, iscover=False):
    '''
    下载所有的id_list 里面的 pid
    返回所有下载成功的pid\n
    如果传入了委托  会在每下载完一个pid时调用  委托会传入一个 pid: str 和 is_success: bool\n
    delegat: method(pid: str, is_success: bool)\n
    '''
    global _opener
    if opener == None:
        if _opener == None:
            opener = _opener = request.build_opener()
        else:
            opener = _opener
        if head == None:
            head = _headtemplate

    success_list = []
    for i, id in enumerate(id_list):
        print(f'list[{i}]: ', end='')

        is_success = download_id(pid=id, dir=dir, headers=head, opener=opener, image_quality=config.get_image_quality(
        ), callback_delegate=callback_delegate, retry=retry, iscover=iscover)
        if is_success:
            success_list.append(id)
        print()

    return success_list


def download_id(pid:str, dir, opener=None, headers=None, image_quality: str = 'original',  callback_delegate: FunctionType = None, retry=3, iscover=False):
    '''
    pid 要下载的pid image_quality图片质量\n
    如果传入了委托  会在函数最后结束时调用 委托会传入一个 pid: str 和 is_success: bool\n
    delegat: method(pid: str, is_success: bool)\n
    用提供的 head 和opener下载 pid中的所有画
    如果没有opener则用request默认opener
    '''

    # 如果没有传入opener 就要自己造一个
    global _opener
    if opener == None:
        if _opener == None:
            opener = _opener = request.build_opener()
        else:
            opener = _opener
        if headers == None:
            headers = _headtemplate

    head = headers.copy()
    print('='*30, f'执行下载{pid}', '='*30)
    info_url = f'https://www.pixiv.net/artworks/{pid}'
    # 抓图片源url 回应图片源json
    src_url = f'https://www.pixiv.net/ajax/illust/{pid}/pages?lang=zh'
    head['referer'] = f'https://www.pixiv.net/artworks/{pid}'
    #description_xpath = '//head/meta[@property="twitter:title"]/@content'

    # 抓取图片信息
    # 包含名字和作者 simple:どちらが好きですか？ by 倉科ゆづき
    requ_info = request.Request(url=info_url, headers=head, method='GET')
    # 开始获取
    info_resp = None
    i = 0
    while i < retry:
        try:
            print(f'times:{i} 获取图片信息from: {info_url}')
            info_resp = opener.open(requ_info)
            break
        except Exception as e:
            print(f'times:{i} {info_url}获取抓取图片信息失败', e)
            if(i == retry - 1):
                if type(callback_delegate) == FunctionType:
                    callback_delegate(pid, False)
                return False
        i += 1

    html_str = info_resp.read().decode()
    # 拿到名字信息
    soup = BeautifulSoup(html_str, 'html.parser')
    tag = soup.select_one('meta[property="twitter:title"]')
    tu_title = tag.attrs.get('content')

    # 抓取图片源
    requ = request.Request(url=src_url, headers=head, method='GET')

    src_resp = None
    i = 0
    while i < retry:
        try:
            print(f'times:{i} 正在获取图片下载源from: {src_url}')
            src_resp = opener.open(requ)
            break
        except Exception as e:
            print(f'times:{i} {src_url}获取图片源失败', e)
            if(i == retry - 1):
                if type(callback_delegate) == FunctionType:
                    callback_delegate(pid, False)
                return False
        i += 1
    re_byte = src_resp.read()
    re_str = re_byte.decode('utf-8')
    temp_data = json.loads(re_str)  # 获得装有图片源的json数据

    # 判断本次下载是否成功
    is_successful = []
    # 遍历获得的json图片源数据
    body = temp_data.get('body')
    # 下载每一个数据源
    for p, item in enumerate(body):
        # 获得下载链接
        tu_url = item.get('urls').get(image_quality)  # 从config 获取想要的图片质量
        suffix = os.path.splitext(tu_url)[1]
        head['referer'] = 'https://www.pixiv.net/'

        # 生成文件名
        filename = f'{pid}_{tu_title}_p{p}{suffix}'
        filename = filename.replace('/', '')
        filename = filename.replace('\\', '')
        filename = filename.replace("'", '')
        filename = filename.replace('"', '')
        filename = filename.replace('?', '')
        filename = filename.replace('*', '')
        filename = filename.replace('<', '')
        filename = filename.replace('>', '')
        print(f'准备下载{filename}')

        # 判断文件覆盖
        if os.path.exists(dir+filename):
            print(f'文件{filename}已经下载过了', end='')

            if iscover:
                print(f'正在重新下载_is_cover: {iscover}')
            else:
                print(f'跳过_is_cover: {iscover}')
                is_successful.append(True)
                continue

        # 判断下载文件夹路径是否正确
        if not os.path.exists(dir):
            os.makedirs(dir)

        # 下载
        trycount = 0
        while trycount < retry:
            try:
                custom_urlretrieve(url=request.Request(tu_url, headers=head), opener=opener, filename=dir +
                                   filename, reporthook=lambda bn,bs,total: illustration.progressbar(bn,bs,total,tu_title))
                print()
                print(f'times:{trycount} from {tu_url} 下载 {filename} 成功')
                is_successful.append(True)
                break
            except Exception as e:
                print(f'times:{trycount} from {tu_url} 下载 {filename} 失败', e)
                if(trycount == retry - 1):
                    is_successful.append(False)
                    break
            trycount += 1

    # ans 本次下载是否成功
    ans = True
    for condition in is_successful:
        ans = ans and condition

    if type(callback_delegate) == FunctionType:
        callback_delegate(pid, ans)

    return ans


def parsing_tutu_data2(jsondata):
    '''
    解析 pixiv_discovery_api2返回的json数据\n
    从中提取出一个推荐pid的列表并返回
    '''
    id_list = []

    re_list = jsondata.get('body').get('recommendedIllusts')
    for item in re_list:
        id_list.append(item.get('illustId'))

    return id_list


def __open_driver_save_cookie():
    '''打开浏览器进行手动登录并且更新本地cookie'''
    discover_page = 'https://www.pixiv.net/discovery'

    print(f'setting browser: {config.get_browser()}')
    # 根据设置获得浏览器 options
    od_dict = custom_driver.get_custom_options_desired_capabilities(
        config.get_browser(), is_proxy=config.get_is_proxies())
    driver = custom_driver.get_custom_driver(
        config.get_browser(), options=od_dict.get('options'))

    print(type(driver))
    # 打开登录页面
    driver.get(url=url.pixiv_login_page)

    # 到登录界面加载完成
    WebDriverWait(driver=driver, timeout=99999).until(
        expected_conditions.title_is('pixiv'))

    # 获得cookie并打印
    cookies = driver.get_cookies()

    # 关闭浏览器
    driver.quit()

    # 保存cookie
    recordcookie.update_local_cookies(newcookies=cookies)


def __force_login():
    forcelogin = config.get_forcelogin()
    print(f'进行检测强制登录  forcelogin: {forcelogin}')
    if not config.get_forcelogin():
        return

    __open_driver_save_cookie()


def __until_linkup(opener=None):
    discoveryjson = None
    while True:
        try:
            print('尝试连接pixiv获取数据')
            print('加载header')
            head = recordcookie.get_head_with_cookie()
            print('连接 pixiv')
            discoveryjson = dicovery_json(head=head, opener=opener)
            break
        except Exception as e:
            print('连接失败,更新cookie', e)
            try:
                __open_driver_save_cookie()
            except Exception as e:
                input(
                    f'selenium 出现问题(大概率是因为浏览器也连不上) 请检查Config.ini 中的代理设置以及驱动版本：{e}')
                return

    # 保存数据
    tool.save_str_data(path.get_ajax_discovery_data_path(),
                       json.dumps(discoveryjson, ensure_ascii=False))
    return discoveryjson


if __name__ == '__main__':
    # headers = recordcookie.get_head_with_cookie()
    # op = config.build_custom_opener()
    # test = illustration('94215843')
    # print(test.get_srclist(op, headers))
    # print(test.get_name(op,headers=headers))
    # test.download(path.get_data_dir(),opener=op,headers=headers)

    # input('done')

    # debug打印
    config.tips()

    # 是否强制执行登录
    __force_login()

    opener = config.build_custom_opener()

    # 直到连接上pixiv 并返回json推荐数据
    discoveryjson = __until_linkup(opener=opener)
    if dicovery_json == None:
        input('没有获取到数据 结束进程')
        sys.exit(1)

    # 开始解析数据
    # 获得id列表
    id_list = parsing_tutu_data2(discoveryjson)
    print(f'pixiv 根据xp推荐 返回了{len(id_list)}个pid ：\n{id_list}')
    # 对比
    id_dict = recordcookie.contrast_with_localrecord(id_list)
    print('其中有', len(id_dict.get('recorded')), '个id已经下载过 : \n', id_dict.get(
        'recorded'), '\n剩余', len(id_dict.get('unrecord')), '个 : \n', id_dict.get('unrecord'))
    need_d = (id_dict.get('unrecord')
              if config.get_skip_recorded() else id_list).copy()
    print(f'skip: {config.get_skip_recorded()} 需要下载{len(need_d)}\n', need_d)
    input('回车确认开始下载')

    # 下载list中的所有pidhua
    print('='*30, '开始下载', '='*30)
    head = recordcookie.get_head_with_cookie()
    success_list = download_idlist(
        id_list=need_d, dir=path.get_tutu_dir(), retry=config.get_retry(), iscover=config.get_is_cover(), opener=opener, head=head, callback_delegate=recordcookie.append_record_pid_local)
    print(f'下载成功数 ：{len(success_list)}')
    print(success_list)
    #

    # 统计失败
    for id in success_list:
        need_d.remove(id)
    print(f'下载失败数{len(need_d)}')
    print(need_d)

    input('done')
