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


pixiv_discovery_api1 = 'https://www.pixiv.net/rpc/recommender.php?type=illust&sample_illusts=auto&num_recommendations=60&page=discovery&mode=all'
pixiv_discovery_api2 = 'https://www.pixiv.net/ajax/discovery/artworks?mode=all&limit=20&lang=zh'


def is_done():
    judge = input('是否完成')
    return True if judge.__eq__('yes') else False


def get_json_data(path: str):
    data = None
    if os.path.exists(path):
        with open(path, 'r') as file:
            data = json.loads(file.read())

    return data


def save_str_data(path: str, json_str: str):
    with open(path, 'w') as file:
        file.write(json_str)


def open_driver_save_cookie():
    pixiv = 'https://www.pixiv.net/'
    pixiv_login_page = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
    discover_page = 'https://www.pixiv.net/discovery'

    driver = None
    print(f'setting browser: {config.get_browser()}')
    if config.get_browser() == 'chrome':
        if os.path.exists(config.chromedriver_exe_path):
            print('加载谷歌驱动')
            driver = webdriver.Chrome()
        else:
            print('缺少谷歌驱动')
    elif config.get_browser() == 'firefox':
        if os.path.exists(config.geckodriver_exe_path):
            print('加载火狐驱动')
            driver = webdriver.Firefox(executable_path=config.geckodriver_exe_path)
        else:
            print('缺少火狐驱动')

    print(type(driver))
    # 打开登录页面
    driver.get(pixiv_login_page)

    #
    WebDriverWait(driver=driver, timeout=10000).until(
        expected_conditions.title_is('pixiv'))

    # 跳转到发现页面
    driver.get(discover_page)

    #WebDriverWait(driver=driver, timeout=10000).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, '_2RNjBox')))
    WebDriverWait(driver=driver, timeout=10000).until(
        expected_conditions.title_is('pixiv'))

    # 获得cookie并打印
    cookies = driver.get_cookies()

    # 关闭浏览器
    driver.quit()

    # 保存cookie
    save_str_data(path=config.cookie_path, json_str=json.dumps(cookies))


def get_head_with_cookie():
    head = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.30',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'referer': 'https://www.pixiv.net/discovery'
    }

    # 添加客制化cookie
    cookiejson = get_json_data(config.cookie_path)
    # 如果没有值的花就直接来个新的
    if type(cookiejson) != list:
        cookiejson = []

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


def dicovery_json(head):

    str_param = {
        'type': 'illust',
        'sample_illusts': 'auto',
        'num_recommendations': '1000',
        'page': 'discovery',
        'mode': 'all'
    }

    para_str = urlencode(str_param)

    head['referer'] = 'https://www.pixiv.net/discovery'

    # 代理
    proxies = {'http': 'http://127.0.0.1:1080',
               'https': 'https://127.0.0.1:1080'}
    prox = request.ProxyHandler(proxies=proxies)

    # opener
    opener = request.build_opener(prox)

    # request
    requ = request.Request(pixiv_discovery_api2, headers=head, method='GET')

    # open
    resp = opener.open(requ)
    print('pixiv: ', resp.getcode())
    r_bt = resp.read()
    r_str = r_bt.decode()
    resp_json = json.loads(r_str)

    return resp_json


def download_idlist(id_list: list, head):
    # 代理
    proxies = {
        'http': 'http://127.0.0.1:1080',
        'https': 'https://127.0.0.1:1080'
    }
    prox = request.ProxyHandler(proxies=proxies)
    # opener
    opener = request.build_opener(prox)

    for id in id_list:
        download_id(pid=id, head=head, opener=opener)


def download_id(pid, head, opener=None):
    # 如果没有传入opener 就要自己造一个
    if opener == None:
        # 代理
        proxies = {'http': 'http://127.0.0.1:1080',
                   'https': 'https://127.0.0.1:1080'}
        prox = request.ProxyHandler(proxies=proxies)

        # opener
        opener = request.build_opener(prox)

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
        return
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
        return
    re_byte = src_resp.read()
    re_str = re_byte.decode('utf-8')
    temp_data = json.loads(re_str)  # 获得装有图片源的json数据

    # 遍历获得的json图片源数据
    body = temp_data.get('body')
    # 下载每一个数据源
    for i, item in enumerate(body):
        # 获得下载链接
        tu_url = item.get('urls').get(
            config.get_image_quality())  # 从config 获取想要的图片质量
        suffix = os.path.splitext(tu_url)[1]
        head['referer'] = 'https://www.pixiv.net/'

        # 生成文件名
        filename = f'{pid}_{tu_title}_p{i}{suffix}'
        print(f'准备下载{filename}')
        if os.path.exists(config.tutu_dir_path+filename):
            print(f'文件{filename}已经下载过了', end='')

            is_cover = config.get_is_cover()

            if is_cover:
                print(f'正在重新下载_is_cover: {is_cover}')
            else:
                print(f'跳过_is_cover: {is_cover}')
                continue

        # 下载
        try:
            ortu_resp = opener.open(request.Request(
                url=tu_url, headers=head, method='GET'))
            # 保存
            with open(config.tutu_dir_path + filename, 'wb') as file:
                file.write(ortu_resp.read())
            print(f'from {tu_url} 下载 {filename} 成功')
        except Exception as e:
            print(f'from {tu_url} 下载 {filename} 失败', e)
            continue


def parsing_tutu_data2(jsondata):
    id_list = []

    re_list = jsondata.get('body').get('recommendedIllusts')
    for item in re_list:
        id_list.append(item.get('illustId'))

    return id_list


def tips():
    print(f'当前cookie_path:{config.cookie_path}')
    print(f'当前发现画廊数据path:{config.tutu_data_path}')
    print(f'当前图图保存位置{config.tutu_dir_path}')
    print(f'需要谷歌驱动位置:{config.chromedriver_exe_path}')
    print(f'需要火狐驱动位置:{config.geckodriver_exe_path}')


def force_login():
    if not config.get_forcelogin():
        return
    
    open_driver_save_cookie()


def until_linkup():
    discoveryjson = None
    while True:
        try:
            print('尝试连接pixiv获取数据')
            head = get_head_with_cookie()
            discoveryjson = dicovery_json(head=head)
            # 保存数据
            with open(config.tutu_data_path, 'w') as file:
                file.write(json.dumps(discoveryjson))
            break
        except Exception as e:
            print('连接失败,更新cookie', e)
            try:
                open_driver_save_cookie()
            except Exception as e:
                input('错误（回车继续）',e)

    return discoveryjson



if __name__ == '__main__':
    tips()

    force_login()

    discoveryjson = until_linkup()

    # 开始解析数据
    # 本地数据
    # tutu_data = get_json_data(config.tutu_data_path)
    # 获得id列表
    id_list = parsing_tutu_data2(discoveryjson)
    print(f'一共{len(id_list)}张图图')
    print(id_list)
    head = get_head_with_cookie()
    print(head)

    #下载list中的所有pidhua
    download_idlist(id_list=id_list, head=head)

    input('done')
