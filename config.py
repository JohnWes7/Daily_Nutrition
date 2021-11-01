import os
import json

# 通过静态方法调用放外面
setting = {
    'image_quality': 'original',  # thumb_mini small regular original
    'is_cover': False,
    'browser': 'chrome',  # firefox
    'forcelogin': False
}


class config:
    # 直接通过属性名调用放里面
    # 文件路径
    cookie_path = os.path.dirname(__file__) + '/data/cookies.json'
    tutu_data_path = os.path.dirname(__file__) + '/data/tutu_list.json'
    chromedriver_exe_path = os.path.dirname(__file__) + '/chromedriver.exe'
    geckodriver_exe_path = os.path.dirname(__file__) + '/geckodriver.exe'
    browsermobproxy_bin_path = os.path.dirname(__file__) + '/browsermob-proxy-2.1.4/bin/browsermob-proxy.bat'

    # 文件夹路径
    data_dir = os.path.dirname(__file__) + '/data/'
    tutu_dir_path = os.path.dirname(__file__) + '/tutu/'
    backgroun_pool_path = tutu_dir_path
    background_dir_path = os.path.dirname(__file__) + '/vs_background/'

    pixiv = 'https://www.pixiv.net/'
    pixiv_login_page = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
    discover_page = 'https://www.pixiv.net/discovery'

    custom_cookie = {
        # 'tag_view_ranking': "RTJMXD26Ak~RcahSSzeRf~jH0uD88V6F~zyKU3Q5L4C~pzzjRSV6ZO~Bd2L9ZBE8q~Ie2c51_4Sp~bopfpc8En6~XDEWeW9f9i~D0nMcn6oGk~Lt-oEicbBr~eVxus64GZU~LJo91uBPz4~7WfWkHyQ76~q303ip6Ui5~QYelAhYfEH~1HSjrqSB3U~Dd2BFtvC_a~BtXd1-LPRH~KN7uxuR89w~aVmLrbYnSr~K8esoIs2eW~-LSsLGmCIU~gVfGX_rH_Y~skx_-I2o4Y~8Q8mLCEW16~tgP8r-gOe_~qUVF3aasqv~PzEXgc_S56~Wka710VIT8~qnGN-oHRQo~D26FCUKCS8~nuuOi_zFTA~ePN3h1AXKX~lQdVtncC-e~X_1kwTzaXt~9V46Zz_N_N~rOnsP2Q5UN~xVHdz2j0kF~cFXtS-flQO~EUwzYuPRbU~2QXu36FK5_~SW0bXgRvYs~lXvRdAunvV~57UnBqevnT~aKhT3n4RHZ~HfqELC_-Q3~Z4hQZu-rU-~_EOd7bsGyl~ziiAzr_h04~_sjpLQz14H~qmix1djJUJ~-StjcwdYwv~jk9IzfjZ6n~QaiOjmwQnI~BSlt10mdnm~gatroTOnfX~MhieHQxNXo~zdx7NJPPfr~y7byyDCjIW~CBKuoUuA6J"
    }

    @staticmethod
    def get_local_cookie():
        with open(config.cookie_path, 'r') as file:
            data = json.loads(file.read())

        return data

    @staticmethod
    def get_image_quality():
        return 'original' if setting.get('image_quality') == None else setting.get('image_quality')

    @staticmethod
    def get_is_cover():
        return False if setting.get('is_cover') == None else setting.get('is_cover')

    @staticmethod
    def get_browser():
        return 'chrome' if setting.get('browser') == None else setting.get('browser')

    @staticmethod
    def get_forcelogin():
        return False if setting.get('forcelogin') == None else setting.get('forcelogin')
