'''
@author : johnwest
@github : https://github.com/JohnWes7/Daily_Nutrition
'''
import json
from urllib import request
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from config import config
import downloads
from src import custom_driver
import re
# 93682182
# 91123048
# 89584897

post_list = []
add_book_url = 'https://www.pixiv.net/ajax/illusts/bookmarks/add'
delete_book_url = 'https://www.pixiv.net/rpc/index.php'
bookmark_event_url = 'https://event.pixiv-recommend.net/\?platform=pc&action=click-bookmark.*'


def analysis_log(log: str, post_data_list: list):
    '''
    解析driver 返回的log提取有用部分加入到
    '''
    params_none = 0
    requ_none = 0

    for item in log:
        message = json.loads(item.get('message')).get('message')

        params = message.get('params')
        if params == None:
            params_none += 1
            continue

        requ = params.get('request')
        if requ == None:
            requ_none += 1
            continue

        if requ.get('url') == None:
            continue

        # 加入收藏时触发
        if requ.get('url').__eq__(add_book_url) and requ.get('method').__eq__("POST"):
            print(requ.get('postData'))
            post_data_list.append(json.loads(requ.get('postData')))

        # 取消收藏时触发
        if requ.get('url').__eq__(delete_book_url) and requ.get('method').__eq__("POST"):
            print(requ.get('postData'))
            try:
                kvlist = requ.get('postData').split('&')
                qs_dict = {}
                for item in kvlist:
                    kvp = item.split('=')
                    qs_dict[kvp[0]] = kvp[1]
                post_data_list.append(qs_dict)
            except Exception as e:
                print(e)

        match = re.match(f'{bookmark_event_url}.*', requ.get('url'))
        if not match == None:
            tempdict = {'url': requ.get('url')}
            post_data_list.append(tempdict)

    print(
        f'analysis: loglen:{log.__len__()}\tparams_none:{params_none}\trequ_none:{requ_none}\tpost_list:{post_list.__len__()}')


def delegate_title_is_pixiv(x: WebDriver):
    '''
    等待用户自行跳转至主页 按照步长执行委托
    处理从浏览器截取的log数据
    '''
    log = []
    log = x.get_log('performance')
    analysis_log(log, post_list)

    title = x.title
    return 'pixiv'.__eq__(title)


def open_discovery():
    # 获取设置
    print('加载配置')
    od_dict = custom_driver.get_custom_options_desired_capabilities(
        config.get_browser(), config.get_is_proxies, True)
    print(od_dict)
    # 生成driver
    print('生成driver')
    driver = custom_driver.get_custom_driver(name=config.get_browser(), options=od_dict.get(
        'options'), desired_capabilities=od_dict.get('desired_capabilities'))
    # driver.maximize_window() # 全屏展开

    print('正在等待网页加载')
    driver.get(config.pixiv)  # 打开网页
    # 加入cookies
    print('加入cookies到浏览器登录')
    cookiejson = downloads.get_json_data(config.cookie_path)
    if type(cookiejson) == list:
        for item in cookiejson:
            try:
                driver.add_cookie(item)
            except Exception as e:
                print('加入cookie时发生: ', e)

    # 刷新
    print('刷新')
    driver.refresh()
    # 等待到主页面
    print('等待到主页面进行跳转到发现，cookie登录失败请进行手动登录')
    WebDriverWait(driver=driver, timeout=99999,
                  poll_frequency=1).until(delegate_title_is_pixiv)
    print('更新本地cookie并跳转')
    cookies = driver.get_cookies()
    downloads.update_local_cookies(cookies)

    # 转到发现页面
    try:
        driver.get(config.discover_page)
        # 等待从发现页面出来然后关闭
        WebDriverWait(driver=driver, timeout=99999,
                      poll_frequency=1).until(delegate_title_is_pixiv)
    except Exception as e:
        print(e)

    print('更新本地cookie')
    cookies = driver.get_cookies()
    downloads.update_local_cookies(cookies)

    driver.quit()


def test():
    # bookmark_event_url2 = 'https://event.pixiv-recommend.net/?platform=pc&action=click-bookmark'
    # sample1 = "https://event.pixiv-recommend.net/?platform=pc&action=click-bookmark&zone=discovery&method=clustering_bqalgc&illust_id=92834061&seed_illust_ids=90553117%2C93470454%2C93623887%2C93790321&login=yes&user_id=25832134&p_ab_id=2&p_ab_id_2=8&p_ab_d_id=773787977"
    # sample2 = 'https://event.pixiv-recommend.net/?platform=pc&action=click-bookmark&zone=discovery&method=clustering_bqalgc&illust_id=91975962&seed_illust_ids=86075831%2C91123048%2C91766083%2C93623887%2C93686296%2C93790321&login=yes&user_id=25832134&p_ab_id=0&p_ab_id_2=2&p_ab_d_id=320056489'
    # match = re.match(
    #     'https://event.pixiv-recommend.net/\?platform=pc&action=click-bookmark.*', sample1)
    # print(match.group())

    # opener = downloads.build_custom_opener()
    # request.urlopen
    # request.urlretrieve
    # request.install_opener

    pass


def get_pid_list():
    d_list = []
    for item in post_list:
        id = item.get('illust_id')
        if not id == None:
            d_list.append(id)

    return d_list


if __name__ == '__main__':

    # 浏览数据
    try:
        open_discovery()
    except Exception as e:
        print(e)
    
    # 保存这次浏览
    downloads.save_str_data(config.bookmarkdata_path, json.dumps(post_list))

    d_list = get_pid_list()
    print(f'开始执行下载\n将要执行下载：{len(d_list)}\n', d_list)

    # 执行下载
    try:
        downloads.download_idlist(
            id_list=d_list, head=downloads.get_head_with_cookie())
    except Exception as e:
        print('下载发生错误 Exception: ', e)

    input('done')