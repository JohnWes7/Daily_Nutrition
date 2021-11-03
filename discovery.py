import json
from os import name
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
# 93682182
# 91123048
# 89584897

log = []

def delegate_title_is_pixiv(x : WebDriver):
    log.extend(x.get_log('performance'))
    print(log.__len__())
    
    title = x.title
    return 'pixiv'.__eq__(title)


def open_discovery():

    # 浏览器设置
    c_option = Options()

    c_option.add_experimental_option('w3c', False)  # 把这个禁用了才能调取所有 log 魔法 必须加
    c_option.add_experimental_option('perfLoggingPrefs', {  # log筛选
        'enableNetwork': True,
        'enablePage': False,
        'traceCategories': 'devtools'  # log 的筛选只跟踪这里面的值 魔法 试出来的 不知道还可以填什么
    })
    caps = {
        'browserName': 'chrome',
        'loggingPrefs': {
            'performance': 'ALL',
            'browser': 'ALL',
        }
    }
    driver = webdriver.Chrome(options=c_option, desired_capabilities=caps)

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

    try:
        driver.get(config.discover_page)
        WebDriverWait(driver=driver, timeout=99999, poll_frequency = 1).until(delegate_title_is_pixiv)
    except Exception as e:
        print(e)

    request_log = driver.get_log('performance')
    for item in request_log:
        temp = json.loads(item.get('message'))
        item['message'] = temp
    downloads.save_str_data(
        path=config.data_dir+'performance_log.json', json_str=json.dumps(request_log))

    driver.quit()


if __name__ == '__main__':
    open_discovery()
    









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
