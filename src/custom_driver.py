'''
@author : johnwest
@github : https://github.com/JohnWes7/Daily_Nutrition
'''
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from config import config
from selenium import webdriver
import os


def options_desired_capabilities_chrome(is_proxy=False, is_getlog=False):
    '''
    返回配置字典\n
    'desired_capabilities' : desired_capabilities\n
    'options' : options\n
    '''
    od_dict = {}
    caps = None
    opt = webdriver.ChromeOptions()
    opt.add_experimental_option(
        'excludeSwitches', ['enable-automation'])  # 禁用浏览器正在被自动化程序控制的提示

    # 是否打开代理
    if is_proxy:
        opt.add_argument(
            f"--proxy-server={config.get_proxies_dict().get('http')}")

    # 是否需要log
    if is_getlog:
        opt.add_experimental_option('w3c', False)  # 把这个禁用了才能调取所有 log 魔法 必须加
        opt.add_experimental_option('perfLoggingPrefs', {  # log筛选
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

    od_dict['desired_capabilities'] = caps
    od_dict['options'] = opt

    return od_dict


def options_desired_capabilities_firefox(is_proxy=False, is_getlog=False):
    '''
    未完工
    '''
    od_dict = {}
    caps = None
    opt = webdriver.FirefoxOptions()

    if is_proxy:
        pass

    if is_getlog:
        pass

    od_dict['desired_capabilities'] = caps
    od_dict['options'] = opt

    return od_dict


def options_desired_capabilities_edge(is_proxy=False, is_getlog=False):
    '''
    返回配置字典\n
    'desired_capabilities' : desired_capabilities\n
    'options' : options\n
    '''
    od_dict = {}
    caps = None
    opt = EdgeOptions()
    opt.use_chromium = True

    #opt.add_experimental_option('excludeSwitches', ['enable-automation'])  # 禁用浏览器正在被自动化程序控制的提示

    # 是否打开代理
    if is_proxy:
        opt.add_argument(
            f"--proxy-server={config.get_proxies_dict().get('http')}")

    # 是否需要log
    if is_getlog:
        opt.add_experimental_option('w3c', False)  # 把这个禁用了才能调取所有 log 魔法 必须加
        opt.add_experimental_option('perfLoggingPrefs', {  # log筛选
            'enableNetwork': True,
            'enablePage': False,
            'traceCategories': 'devtools'  # log 的筛选只跟踪这里面的值 魔法 试出来的 不知道还可以填什么
        })
        caps = {
            'browserName': 'ms',
            'loggingPrefs': {
                'performance': 'ALL',
                'browser': 'ALL',
            }
        }

    od_dict['desired_capabilities'] = caps
    od_dict['options'] = opt

    return od_dict


def get_custom_options_desired_capabilities(name: str, is_proxy=False, is_getlog=False) -> dict:
    '''
    返回配置字典\n
    'desired_capabilities' : desired_capabilities\n
    'options' : options\n
    '''
    name_od_func = {
        'chrome': options_desired_capabilities_chrome,
        'firefox': options_desired_capabilities_firefox,
        'edge':options_desired_capabilities_edge
    }

    return name_od_func.get(name)(is_proxy, is_getlog)


def custom_chrome(options=None, desired_capabilities=None) -> WebDriver:
    if os.path.exists(config.chromedriver_exe_path):
        print('加载谷歌驱动')
        driver = webdriver.Chrome(
            options=options, desired_capabilities=desired_capabilities)
        return driver

    print('缺少谷歌驱动', config.chromedriver_exe_path)


def custom_firefox(options=None, desired_capabilities=None) -> WebDriver:
    if os.path.exists(config.geckodriver_exe_path):
        print('加载火狐驱动')
        driver = webdriver.Firefox(executable_path=config.geckodriver_exe_path,
                                   options=options, desired_capabilities=desired_capabilities)
        return driver

    print('缺少火狐驱动', config.geckodriver_exe_path)


def custom_edge(options=None, desired_capabilities=None):
    if os.path.exists(config.chromedriver_exe_path):
        print('加载edge驱动')
        driver = webdriver.Edge(
            options=options, capabilities=desired_capabilities)
        return driver

    print('缺少edge驱动', config.edgedriver_exe_path)


def get_custom_driver(name: str, options=None, desired_capabilities=None) -> WebDriver:
    name_driver_func = {
        'chrome': custom_chrome,
        'firefox': custom_firefox,
        'edge':custom_edge
    }

    driver = name_driver_func.get(name)(options, desired_capabilities)
    return driver
