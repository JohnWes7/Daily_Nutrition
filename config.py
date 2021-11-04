import os
import json
import configparser

# 创文件夹（防止被删）
datadir = os.path.dirname(__file__) + '/data/'
if not os.path.exists(datadir):
    os.makedirs(datadir)
defaultutudir = os.path.dirname(__file__) + '/tutu/'
if not os.path.exists(defaultutudir):
    os.makedirs(defaultutudir)

# 通过静态方法调用放外面
# 默认设置
default_setting = {
    'image_quality': 'original',    # thumb_mini small regular original 图片质量
    'is_cover': False,              # 是否覆盖
    'browser': 'chrome',            # firefox
    'forcelogin': False,            # 是否强制登录
    'download_path' : defaultutudir,# 下载文件夹
    'is_proxies' : True,            # 是否启用代理
    'proxies' : {                   # 代理
        'http': 'http://127.0.0.1:1080',
        'https': 'https://127.0.0.1:1080'
    },
    'mode' : 'save',
    'limit' : 60,
    'lang' : 'zh',
    'skip_recorded' : True
}

# section名称
ads = 'auto_download_setting'
link = 'link'

# 读取Config.ini
conf_path = os.path.dirname(__file__) + '/Config.ini'
conf = configparser.ConfigParser()
conf.read(conf_path, encoding='utf-8')


class config:
    # 直接通过属性名调用 不可更改
    # 文件路径
    cookie_path = os.path.dirname(__file__) + '/data/cookies.json'
    ajax_discovery_data_path = os.path.dirname(__file__) + '/data/wwwpixivnet_ajax_discovery_artworks.json'
    download_record_path = os.path.dirname(__file__) + '/data/downloadrecord.json'
    # 驱动位置
    chromedriver_exe_path = os.path.dirname(__file__) + '/driver/chromedriver.exe'
    geckodriver_exe_path = os.path.dirname(__file__) + '/geckodriver.exe'
    edgedriver_exe_path = os.path.dirname(__file__) + '/driver/msedgedriver.exe'
    # 文件夹路径
    data_dir = datadir


    #自定义cookie 现在只能在代码这里加入
    custom_cookie = {

    }


    pixiv = 'https://www.pixiv.net/'
    pixiv_login_page = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
    discover_page = 'https://www.pixiv.net/discovery'

    @staticmethod
    def get_local_cookie():
        with open(config.cookie_path, 'r') as file:
            data = json.loads(file.read())

        return data

    @staticmethod
    def get_image_quality():
        image_quality = conf.get(
            ads, 'image_quality', fallback=default_setting.get('image_quality'))
        if image_quality.__eq__('thumb_mini') or image_quality.__eq__('small') or image_quality.__eq__('regular') or image_quality.__eq__('original'):
            return image_quality

        return default_setting.get('image_quality')

    @staticmethod
    def get_is_cover():
        is_cover = conf.getboolean(
            ads, 'is_cover', fallback=default_setting.get('is_cover'))
        return is_cover

    @staticmethod
    def get_browser():
        browser = conf.get(
            link, 'browser', fallback=default_setting.get('browser'))
        if browser.__eq__('chrome') or browser.__eq__('firefox'):
            return browser

        return default_setting.get('browser')

    @staticmethod
    def get_forcelogin():
        forcelogin = conf.getboolean(
            ads, 'forcelogin', fallback=default_setting.get('forcelogin'))
        return forcelogin
    
    @staticmethod
    def get_ads_download_path():
        path = conf.get(ads, 'download_path', fallback=default_setting.get('download_path'))
        if os.path.exists(path=path):
            if path[path.__len__() - 1].__eq__('/'):
                return path
            return path + '/'
        return default_setting.get('download_path')

    @staticmethod
    def get_is_proxies():
        is_proxies = conf.getboolean(
            link, 'is_proxies', fallback=default_setting.get('is_proxies'))
        return is_proxies
    
    @staticmethod
    def get_proxies_dict():
        http = conf.get(link, 'http', fallback='http://127.0.0.1:1080')
        https = conf.get(link, 'https', fallback='https://127.0.0.1:1080')

        proxies_dict = {
            'http' : http,
            'https' : https
        }
        return proxies_dict
    
    @staticmethod
    def get_discovery_query_dict():
        qd = {}

        mode = conf.get(ads, 'mode', fallback=default_setting.get('mode'))
        if mode.__eq__('save') or mode.__eq__('all') or mode.__eq__('r18'):
            qd['mode'] = mode
        else:
            qd['mode'] = default_setting.get('mode')
        
        limit = conf.getint(ads, 'limit', fallback=default_setting.get('limit'))
        qd['limit'] = limit

        lang = conf.get(ads, 'lang', fallback=default_setting.get('lang'))
        if lang.__eq__('en') or lang.__eq__('ko') or lang.__eq__('zh') or lang.__eq__('zh_tw') or lang.__eq__('romaji'):
            qd['lang'] = lang
        else:
            qd['lang'] = default_setting.get('lang')
        
        return qd

    @staticmethod
    def get_skip_recorded():
        skip_recorded = conf.getboolean(ads, 'skip_recorded', fallback=default_setting.get('skip_recorded'))
        return skip_recorded
