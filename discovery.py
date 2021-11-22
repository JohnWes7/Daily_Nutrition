'''
@author : johnwest
@github : https://github.com/JohnWes7/Daily_Nutrition
'''
from src import tool
if __name__=='__main__':
    tool.check()
import json
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from config import url
from config import path
from config import config
from config import recordcookie
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

    
    return x.current_url.__eq__('https://www.pixiv.net/stacc?mode=unify')


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
    driver.get(url.get_pixiv())  # 打开网页
    # 加入cookies
    print('加入cookies到浏览器登录')
    cookiejson = tool.get_json_data(path.get_cookie_path())
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
    WebDriverWait(driver=driver, timeout=99999).until(expected_conditions.title_is('pixiv'))
    print('更新本地cookie并跳转')
    cookies = driver.get_cookies()
    recordcookie.update_local_cookies(cookies)

    
    try:
        # 转到发现页面
        driver.get(url.get_discover_page())
        # 等待从发现页面出来然后关闭
        WebDriverWait(driver=driver, timeout=99999,
                      poll_frequency=1).until(delegate_title_is_pixiv)
        print('更新本地cookie')
        cookies = driver.get_cookies()
        recordcookie.update_local_cookies(cookies)
    except Exception as e:
        print(e)
    

    driver.quit()


def get_pid_list() -> list[downloads.illustration]:
    d_list = []
    global post_list
    for item in post_list:
        id = item.get('illust_id')
        if id:
            d_list.append(downloads.illustration(id))
            
    return d_list


if __name__ == '__main__':
    # 浏览数据
    try:
        open_discovery()
    except Exception as e:
        print(e)
    
    # 保存这次浏览
    tool.save_str_data(path.get_bookmarkdata_path(), json.dumps(post_list))

    #打印
    d_list = get_pid_list()
    print(f'开始执行下载\n将要执行下载：{len(d_list)}\nlist:')
    for tu in d_list:
        print(tu.id,end=' ')
    print()

    input('按下回车开始下载')
    # 执行下载
    opener = config.build_custom_opener()
    headers = recordcookie.get_head_with_cookie()
    for tu in d_list:
        print('='*30,tu.id,'='*30)

        print('尝试插画信息')
        for i in range(config.get_retry()):
            try:
                print(f'access num:{i}',tu.get_name(opener=opener,headers=headers))
                break
            except Exception as e:
                print(e)
        
        print('尝试获取图片源')
        for i in range(config.get_retry()):
            try:
                print(f'access num:{i}')
                temp = tu.get_srclist(opener=opener,headers=headers)
                for i,p in enumerate(temp):
                    print(f'p{i}:',p.get('urls').get(config.get_image_quality()))
                break
            except Exception as e:
                print(e)
        
        print('尝试下载')
        for i in range(config.get_retry()):
            try:
                print(f'access num:{i}')
                tu.download(path.get_tutu_dir(),opener=opener,headers=headers,image_quality=config.get_image_quality())
                break
            except Exception as e:
                print(e)
        print()
    input('done')