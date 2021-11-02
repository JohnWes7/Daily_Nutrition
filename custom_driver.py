from selenium.webdriver.remote.webdriver import WebDriver
from config import config
from selenium import webdriver
import os


def custom_chrome() -> WebDriver:
    if os.path.exists(config.chromedriver_exe_path):
        print('加载谷歌驱动')
        driver = webdriver.Chrome()
        return driver

    print('缺少谷歌驱动')
    


def custom_firefox() -> WebDriver:
    if os.path.exists(config.geckodriver_exe_path):
        print('加载火狐驱动')
        driver = webdriver.Firefox(executable_path=config.geckodriver_exe_path)
        return driver

    print('缺少火狐驱动')
    


def get_custom_driver(name) -> WebDriver:
    name_driver_func = {
        'chrome': custom_chrome,
        'firefox': custom_firefox
    }

    driver = name_driver_func.get(name)()
    return driver
