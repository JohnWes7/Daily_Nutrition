'''
@author : johnwest
@github : https://github.com/JohnWes7/Daily_Nutrition
'''
import json
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options as fire_fox_Optin
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import wait
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from config import config
# from browsermobproxy import Server
import downloads
import custom_driver
# 93682182
# 91123048
# 89584897

post_list = []
add_book_url = 'https://www.pixiv.net/ajax/illusts/bookmarks/add'
delete_book_url = 'https://www.pixiv.net/rpc/index.php' 


def analysis_log(log: str):
    pass


def delegate_title_is_pixiv(x: WebDriver):
    '''
    等待用户自行跳转至主页 按照步长执行委托
    处理从浏览器截取的log数据
    '''
    log = x.get_log('performance')
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

        if requ.get('url').__eq__(add_book_url) and requ.get('method').__eq__("POST"):
            print(requ.get('postData'))
            post_list.append(json.loads(requ.get('postData')))
        
        if requ.get('url').__eq__(delete_book_url) and requ.get('method').__eq__("POST"):
            print(requ.get('postData'))
            try:
                kvlist = requ.get('postData').split('&')
                qs_dict = {}
                for item in kvlist:
                    kvp = item.split('=')
                    qs_dict[kvp[0]] = kvp[1]
                post_list.append(qs_dict)
            except Exception as e:
                print(e)

            
    print(f'analysis: loglen:{log.__len__()}\tparams_none:{params_none}\trequ_none:{requ_none}\tpost_list:{post_list.__len__()}')

    title = x.title
    return 'pixiv'.__eq__(title)


def open_discovery():

    # 弃用浏览器设置
        # c_option = Options()
        # c_option.add_experimental_option('w3c', False)  # 把这个禁用了才能调取所有 log 魔法 必须加
        # c_option.add_experimental_option('perfLoggingPrefs', {  # log筛选
        #     'enableNetwork': True,
        #     'enablePage': False,
        #     'traceCategories': 'devtools'  # log 的筛选只跟踪这里面的值 魔法 试出来的 不知道还可以填什么
        # })
        # caps = {
        #     'browserName': 'chrome',
        #     'loggingPrefs': {
        #         'performance': 'ALL',
        #         'browser': 'ALL',
        #     }
        # }
    od_dict = custom_driver.get_custom_options_desired_capabilities(
        config.get_browser(), config.get_is_proxies, True)
    driver = webdriver.Chrome(options=od_dict.get(
        'options'), desired_capabilities=od_dict.get('desired_capabilities'))
    # driver.maximize_window() # 全屏展开

    driver.get(config.pixiv)  # 打开网页
    # 加入cookies
    cookiejson = config.get_local_cookie()
    for item in cookiejson:
        try:
            driver.add_cookie(item)
        except Exception as e:
            print('加入cookie时发生: ', e)
    # 刷新
    driver.refresh()

    # 转到发现页面
    try:
        driver.get(config.discover_page)
        # 等待从发现页面出来然后关闭
        WebDriverWait(driver=driver, timeout=99999,poll_frequency=1).until(delegate_title_is_pixiv)
    except Exception as e:
        print(e)

    last_request_log = driver.get_log('performance')
    print('last_log len: ', len(last_request_log))

    downloads.save_str_data(path=config.data_dir +'post_list.json', json_str=json.dumps(post_list))

    driver.quit()


if __name__ == '__main__':
    open_discovery()
    
    print('开始执行下载')



# 弃用
# 用不了梯子 弃用
    # BMPServer = Server(config.browsermobproxy_bin_path)
    # BMPServer.start()
    # BMPproxy = BMPServer.create_proxy()
    # #driver 驱动
    # chrome_option = Options()
    # # 禁用扩展插件,是魔法,不然报错。
    # chrome_option.add_argument('--ignore-certificate-errors')
    # # BMPproxy.proxy返回的是localhost:8081端口
    # chrome_option.add_argument('--proxy-server={}'.format(BMPproxy.proxy))
# log_type1 = 'browser'
    # log_type2 = 'driver'
    # log_type3 = 'client'
    # log_type4 = 'server'

    # cookiedata = driver.get_cookies()
    # try:
    #     driver_log1 = driver.get_log(log_type1)
    # except Exception as e:
    #     print(e)
    # try:
    #     driver_log2 = driver.get_log(log_type2)
    # except Exception as e:
    #     print(e)
    # try:
    #     driver_log3 = driver.get_log(log_type3)
    # except Exception as e:
    #     print(e)
    # try:
    #     driver_log4 = driver.get_log(log_type4)
    # except Exception as e:
    #     print(e)

    # print(type(driver_log1),driver_log1)

    # downloads.save_str_data(
    #     path=config.data_dir+f'{log_type1}_log.json', json_str=json.dumps(driver_log1))
    # downloads.save_str_data(
    #     path=config.data_dir+f'{log_type2}_log.json', json_str=json.dumps(driver_log2))
    # downloads.save_str_data(
    #     path=config.data_dir+f'{log_type3}_log.json', json_str=json.dumps(driver_log3))
    # downloads.save_str_data(
    #     path=config.data_dir+f'{log_type4}_log.json', json_str=json.dumps(driver_log4))
    # print(cookiedata)
