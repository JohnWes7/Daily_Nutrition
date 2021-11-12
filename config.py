'''
@author : johnwest
@github : https://github.com/JohnWes7/Daily_Nutrition
config类因为没有get;所以全部包装成方法防止被修改好了
'''
import os
import json
import configparser



class path:
    # 直接通过属性名调用 不可更改
    # 文件路径
    # cookie_path = os.path.dirname(__file__) + '/data/cookies.json'
    # ajax_discovery_data_path = os.path.dirname(__file__) + '/data/wwwpixivnet_ajax_discovery_artworks.json'
    # download_record_path = os.path.dirname(__file__) + '/data/downloadrecord.json'
    # performance_log_path = os.path.dirname(__file__) + '/data/performance.json'
    # bookmarkdata_path = os.path.dirname(__file__) + '/data/bookmarkdata.json'
    # # 驱动位置
    # chromedriver_exe_path = os.path.dirname(__file__) + '/chromedriver.exe'
    # geckodriver_exe_path = os.path.dirname(__file__) + '/driver/geckodriver.exe'
    # edgedriver_exe_path = os.path.dirname(__file__) + '/msedgedriver.exe'
    # # 文件夹路径
    # data_dir = datadir
    # data_temp_dir = data_dir + 'temp/'

    # 文件路径
    @staticmethod
    def get_cookie_path():
        '''cookie文件路径'''
        return os.path.dirname(__file__) + '/data/cookies.json'
    @staticmethod
    def get_ajax_discovery_data_path():
        '''向推荐页面请求的推荐数据保存路径'''
        return os.path.dirname(__file__) + '/data/wwwpixivnet_ajax_discovery_artworks.json'
    @staticmethod
    def get_download_record_path():
        '''下载过的图的记录数据路径'''
        return os.path.dirname(__file__) + '/data/downloadrecord.json'
    @staticmethod
    def get_performance_log_path():
        '''浏览器log文件保存路径'''
        return os.path.dirname(__file__) + '/data/performance.json'
    @staticmethod
    def get_bookmarkdata_path():
        '''调用add网络请求的记录'''
        return os.path.dirname(__file__) + '/data/bookmarkdata.json'
    
    # 驱动位置
    @staticmethod
    def get_chromedriver_exe_path():
        '''谷歌驱动路径'''
        return os.path.dirname(__file__) + '/chromedriver.exe'
    @staticmethod
    def get_geckodriver_exe_path():
        '''火狐驱动路径'''
        return os.path.dirname(__file__) + '/driver/geckodriver.exe'
    @staticmethod
    def get_edgedriver_exe_path():
        '''edge驱动路径'''
        return os.path.dirname(__file__) + '/msedgedriver.exe'
    
    # 文件夹路径
    @staticmethod
    def get_data_dir():
        '''data文件夹路径'''
        return os.path.dirname(__file__) + '/data/'
    @staticmethod
    def get_data_temp_dir():
        '''temp文件夹路径'''
        return path.get_data_dir() + 'temp/'
    @staticmethod
    def getcwd():
        '''获得环境文件夹路径'''
        return os.path.dirname(__file__) + '/'
    @staticmethod
    def get_tutu_dir():
        return os.path.dirname(__file__) + '/tutu/'


class url:
    pixiv = 'https://www.pixiv.net/'
    pixiv_login_page = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
    discover_page = 'https://www.pixiv.net/discovery'
    @staticmethod
    def get_pixiv():
        return 'https://www.pixiv.net/'
    @staticmethod
    def get_pixiv_login_page():
        return 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
    @staticmethod
    def get_discover_page():
        return 'https://www.pixiv.net/discovery'



# 通过静态方法调用放外面
# 默认设置
default_setting = {
    'image_quality': 'original',    # thumb_mini small regular original 图片质量
    'is_cover': False,              # 是否覆盖
    'browser': 'edge',              # firefox chrome
    'forcelogin': False,            # 是否强制登录
    'download_path' : path.get_tutu_dir(),# 下载文件夹
    'is_proxies' : True,            # 是否启用代理
    'proxies' : {                   # 代理
        'http': 'http://127.0.0.1:1080',
        'https': 'https://127.0.0.1:1080'
    },
    'mode' : 'save',
    'limit' : 60,
    'lang' : 'zh',
    'skip_recorded' : True,
    'retry' : 3
}

# 读取Config.ini
conf_path = os.path.dirname(__file__) + '/Config.ini'
conf = configparser.ConfigParser()
conf.read(conf_path, encoding='utf-8')

# section名称
ads = 'auto_download_setting'
link = 'link'

class config:
    '''设置类获得所有ini里面的设置'''

    #自定义cookie 现在只能在代码这里加入 基本放弃
    custom_cookie = {

    }

    @staticmethod
    def get_local_cookie():
        '''获得本地cookie 这方法随便塞的地方'''
        with open(config.cookie_path, 'r', encoding='utf-8') as file:
            data = json.loads(file.read())

        return data

    @staticmethod
    def get_image_quality():
        '''获取图片质量'''
        image_quality = conf.get(
            ads, 'image_quality', fallback=default_setting.get('image_quality'))
        if image_quality.__eq__('thumb_mini') or image_quality.__eq__('small') or image_quality.__eq__('regular') or image_quality.__eq__('original'):
            return image_quality

        return default_setting.get('image_quality')

    @staticmethod
    def get_is_cover():
        '''获取是否被覆盖'''
        is_cover = conf.getboolean(
            ads, 'is_cover', fallback=default_setting.get('is_cover'))
        return is_cover

    @staticmethod
    def get_browser():
        '''获取设置的浏览器'''
        browser = conf.get(
            link, 'browser', fallback=default_setting.get('browser'))
        if browser.__eq__('chrome') or browser.__eq__('firefox') or browser.__eq__('edge'):
            return browser

        return default_setting.get('browser')

    @staticmethod
    def get_forcelogin():
        '''获取是否强制登录'''
        forcelogin = conf.getboolean(
            ads, 'forcelogin', fallback=default_setting.get('forcelogin'))
        return forcelogin
    
    @staticmethod
    def get_ads_download_path():
        '''获取设置的下载位置'''
        path = conf.get(ads, 'download_path', fallback=default_setting.get('download_path'))
        if os.path.exists(path=path):
            if path[path.__len__() - 1].__eq__('/'):
                return path
            return path + '/'
        return default_setting.get('download_path')

    @staticmethod
    def get_is_proxies():
        '''获取是否打开代理'''
        is_proxies = conf.getboolean(
            link, 'is_proxies', fallback=default_setting.get('is_proxies'))
        return is_proxies
    
    @staticmethod
    def get_proxies_dict():
        '''获取代理的地址和端口字典'''
        http = conf.get(link, 'http', fallback='http://127.0.0.1:1080')
        https = conf.get(link, 'https', fallback='https://127.0.0.1:1080')

        proxies_dict = {
            'http' : http,
            'https' : https
        }
        return proxies_dict
    
    @staticmethod
    def get_discovery_query_dict():
        '''获取需要请求的查询字符串'''
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
        '''获取是否跳过记录的id项'''
        skip_recorded = conf.getboolean(ads, 'skip_recorded', fallback=default_setting.get('skip_recorded'))
        return skip_recorded
    
    @staticmethod
    def get_retry():
        '''获取重试次数'''
        retry = conf.getint(ads,'retry', fallback=default_setting.get('retry'))
        return retry

# 创文件夹（防止被删）
if not os.path.exists(path.get_data_dir()):
    os.makedirs(path.get_data_dir())
if not os.path.exists(path.get_tutu_dir()):
    os.makedirs(path.get_tutu_dir())