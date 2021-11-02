'''
@author : johnwest
@github : 
'''
from typing import Any
from urllib import request
from urllib.parse import urlencode
from selenium import webdriver
from selenium.webdriver.support import wait
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from lxml import etree
from config import config
import json
import os
import sys
import custom_driver


pixiv_discovery_api1 = 'https://www.pixiv.net/rpc/recommender.php?type=illust&sample_illusts=auto&num_recommendations=60&page=discovery&mode=all'
pixiv_discovery_api2 = 'https://www.pixiv.net/ajax/discovery/artworks'


def get_json_data(path: str):
    data = None
    if os.path.exists(path):
        with open(path, 'r', encoding='utf8') as file:
            data = json.loads(file.read())

    return data


def save_str_data(path: str, json_str: str):
    with open(path, 'w', encoding='utf8') as file:
        file.write(json_str)


def update_cookies(oldcookies: list, newcookies: list) -> list:
    '''
    更新cookie 返回用新cookie更新后的cookie数据
    '''
    oldcopy = oldcookies.copy()
    add = []
    for new in newcookies:
        isadd = True
        for old in oldcopy:
            if old.get('name').__eq__(new.get('name')):
                old.update(new)
                isadd = False
                break
        if isadd:
            add.append(new)

    oldcopy.extend(add)
    return oldcopy


def update_local_cookies(newcookies: list):
    '''
    用新cookie 更新到本地
    '''
    oldcookie = get_json_data(config.cookie_path)
    if oldcookie == None:
        # 如果先前没有值直接保存
        oldcookie = newcookies
    else:
        oldcookie = update_cookies(oldcookie, newcookies)
    save_str_data(config.cookie_path, json_str=json.dumps(oldcookie))


def open_driver_save_cookie():
    pixiv_login_page = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
    discover_page = 'https://www.pixiv.net/discovery'

    print(f'setting browser: {config.get_browser()}')
    driver = custom_driver.get_custom_driver(config.get_browser())

    print(type(driver))
    # 打开登录页面
    driver.get(pixiv_login_page)

    # 到登录界面加载完成
    WebDriverWait(driver=driver, timeout=99999).until(
        expected_conditions.title_is('pixiv'))

    # 跳转到发现页面
    # driver.get(discover_page)

    # WebDriverWait(driver=driver, timeout=10000).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, '_2RNjBox')))
    # WebDriverWait(driver=driver, timeout=10000).until(
    #     expected_conditions.title_is('pixiv'))

    # 获得cookie并打印
    cookies = driver.get_cookies()

    # 关闭浏览器
    driver.quit()

    # 保存cookie TODO:cookie不删除重写保存
    update_local_cookies(newcookies=cookies)


def get_head_with_cookie():
    head = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.30',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'referer': 'https://www.pixiv.net/discovery'
    }

    cookiejson = get_json_data(config.cookie_path)
    # 如果没有值的花就直接来个新的
    if type(cookiejson) != list:
        cookiejson = []

    # 添加客制化cookie
    for name in config.custom_cookie.keys():
        tempdict = {}
        tempdict['name'] = name
        tempdict['value'] = config.custom_cookie.get(name)

        cookiejson.append(tempdict)

    # 添加已经抓取的cookie到head
    cookiestr = ''
    for i, item in enumerate(cookiejson):
        name = item.get('name')
        value = item.get('value')
        temp = None
        if i == 0:
            temp = f'{name}={value}'
        else:
            temp = f'; {name}={value}'
        cookiestr += temp

    head['cookie'] = cookiestr

    return head


def build_custom_opener() -> request.OpenerDirector:
    if config.get_is_proxies():
        # 代理
        proxies = config.get_proxies_dict()
        prox = request.ProxyHandler(proxies=proxies)
        # opener
        opener = request.build_opener(prox)
        return opener
    else:
        opener = request.build_opener()
        return opener


def dicovery_json(head):
    # 更改header
    head['referer'] = 'https://www.pixiv.net/discovery'

    # 获得查询字符串
    qd = config.get_discovery_query_dict()
    query_string = urlencode(qd)

    opener = build_custom_opener()

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


def download_idlist(id_list: list, head):
    '''
    下载所有的id_list 里面的 pid
    返回所有下载成功的pid
    '''
    opener = build_custom_opener()

    success_list = []
    for id in id_list:
        is_success = download_id(pid=id, head=head, opener=opener, image_quality=config.get_image_quality())
        if is_success:
            success_list.append(id)

    return success_list


def download_id(pid, head, image_quality: str = 'original', opener=None):
    '''
    用提供的 head 和opener下载 pid中的所有画
    如果没有opener则用build_custom_opener()生成一个新的
    '''

    # 如果没有传入opener 就要自己造一个
    if opener == None:
        opener = build_custom_opener()

    info_url = f'https://www.pixiv.net/artworks/{pid}'
    # 抓图片源url 回应图片源json
    src_url = f'https://www.pixiv.net/ajax/illust/{pid}/pages?lang=zh'
    head['referer'] = f'https://www.pixiv.net/artworks/{pid}'
    description_xpath = '//head/meta[@property="twitter:title"]/@content'

    # 抓取图片信息
    # 包含名字和作者 simple:どちらが好きですか？ by 倉科ゆづき
    requ_info = request.Request(url=info_url, headers=head, method='GET')
    # 开始获取
    info_resp = None
    try:
        print(f'正在获取图片信息from: {info_url}')
        info_resp = opener.open(requ_info)
    except Exception as e:
        print(f'{info_url}获取抓取图片信息失败', e)
        return False
    html_str = info_resp.read().decode()
    e = etree.HTML(html_str)
    # 拿到有信息的 description
    tu_title = e.xpath(description_xpath)

    # 抓取图片源
    requ = request.Request(url=src_url, headers=head, method='GET')
    src_resp = None
    try:
        print(f'正在获取图片下载源from: {src_url}')
        src_resp = opener.open(requ)
    except Exception as e:
        print(f'{src_url}获取图片源失败', e)
        return False
    re_byte = src_resp.read()
    re_str = re_byte.decode('utf-8')
    temp_data = json.loads(re_str)  # 获得装有图片源的json数据

    # 判断本次下载是否成功
    is_successful = []
    # 遍历获得的json图片源数据
    body = temp_data.get('body')
    # 下载每一个数据源
    for i, item in enumerate(body):
        # 获得下载链接
        tu_url = item.get('urls').get(image_quality)  # 从config 获取想要的图片质量
        suffix = os.path.splitext(tu_url)[1]
        head['referer'] = 'https://www.pixiv.net/'

        # 生成文件名
        filename = f'{pid}_{tu_title}_p{i}{suffix}'
        print(f'准备下载{filename}')
        if os.path.exists(config.get_ads_download_path()+filename):
            print(f'文件{filename}已经下载过了', end='')

            is_cover = config.get_is_cover()

            if is_cover:
                print(f'正在重新下载_is_cover: {is_cover}')
            else:
                print(f'跳过_is_cover: {is_cover}')
                is_successful.append(True)
                continue

        # 下载
        try:
            ortu_resp = opener.open(request.Request(
                url=tu_url, headers=head, method='GET'))
            # 保存
            with open(config.get_ads_download_path() + filename, 'wb') as file:
                file.write(ortu_resp.read())
            print(f'from {tu_url} 下载 {filename} 成功')
            is_successful.append(True)
        except Exception as e:
            print(f'from {tu_url} 下载 {filename} 失败', e)
            is_successful.append(False)
            continue

    ans = True
    for condition in is_successful:
        ans = ans and condition
    return ans


def parsing_tutu_data2(jsondata):
    id_list = []

    re_list = jsondata.get('body').get('recommendedIllusts')
    for item in re_list:
        id_list.append(item.get('illustId'))

    return id_list


def tips():
    print('='*30, 'Tips', '='*30)
    print('当前设置:')
    print(f'图片质量image_quality : {config.get_image_quality()}')
    print(f'是否覆盖is_cover : {config.get_is_cover()}')
    print(f'浏览器browser : {config.get_browser()}')
    print(f'是否强制登录forcelogin : {config.get_forcelogin()}')
    print(f'下载保存路径download_path : {config.get_ads_download_path()}')
    print(f'代理 is_proxies : {config.get_is_proxies()}')
    print(config.get_proxies_dict())
    print(f'api查询字符串参数：\n{config.get_discovery_query_dict()}')
    print(f'cookie_path:{config.cookie_path}')
    print(f'discovery返回数据path:{config.ajax_discovery_data_path}')
    print(f'需要谷歌驱动位置:{config.chromedriver_exe_path}')
    print(f'需要火狐驱动位置:{config.geckodriver_exe_path}')
    print('='*60)


def force_login():
    forcelogin = config.get_forcelogin()
    print(f'进行检测强制登录  forcelogin: {forcelogin}')
    if not config.get_forcelogin():
        return

    open_driver_save_cookie()


def until_linkup():
    discoveryjson = None
    while True:
        try:
            print('尝试连接pixiv获取数据')
            print('加载header')
            head = get_head_with_cookie()
            print('连接 pixiv')
            discoveryjson = dicovery_json(head=head)
            break
        except Exception as e:
            print('连接失败,更新cookie', e)
            try:
                open_driver_save_cookie()
            except Exception as e:
                input('selenium 出现问题(大概率是因为浏览器也连不上)：', e)
                return

    # 保存数据
    save_str_data(config.ajax_discovery_data_path,
                  json.dumps(discoveryjson, ensure_ascii=False))
    return discoveryjson



def contrast_with_localrecord(id_list: list):
    '''
    和本地下载记录对比 返回一个字典包含了 
    record：本地下载列表
    unrecord：对比之后发现没有被记录的
    recorded：已经被记录过的项
    '''
    record = get_json_data(config.download_record_path)
    if record == None:
        record = []
    
    filtrate_list = []
    final_list = []
    for id in id_list:
        if id in record:
            filtrate_list.append(id)
        else:
            final_list.append(id)
    
    




if __name__ == '__main__':
    tips()

    record = get_json_data(config.download_record_path)
    if record == None:
        record = []

    # 是否强制执行登录
    force_login()

    # 直到连接上pixiv 并返回json推荐数据
    discoveryjson = until_linkup()
    if dicovery_json == None:
        input('没有获取到数据 结束进程')
        sys.exit(1)


    # 开始解析数据
    # 获得id列表
    id_list = parsing_tutu_data2(discoveryjson)
    print(f'pixiv 根据xp推荐 返回了{len(id_list)}个pid ：')
    print(id_list)
    filtrate_list = []
    final_list = []
    for id in id_list:
        if id in record:
            filtrate_list.append(id)
        else:
            final_list.append(id)
    print(f'其中有{len(filtrate_list)}个id已经下载过 : ')
    print(filtrate_list)
    print(f'剩余{len(final_list)}个 : ')
    print(final_list)
    input('回车确认开始下载')

    
    # 下载list中的所有pidhua
    print('='*30, '开始下载', '='*30)
    head = get_head_with_cookie()
    success_list = download_idlist(id_list=final_list, head=head)
    print(f'下载成功数 ：{len(success_list)}')
    print(success_list)

    #统计失败
    for id in success_list:
        final_list.remove(id)
    print(f'下载失败数{len(final_list)}')
    print(final_list)


    #保存已经下载过的列表
    record.extend(success_list)
    save_str_data(config.download_record_path, json.dumps(record))

    input('done')
