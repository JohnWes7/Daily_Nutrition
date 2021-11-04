'''
@author : johnwest
@github : https://github.com/JohnWes7/Daily_Nutrition
'''
import json
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
        
        #加入收藏时触发
        if requ.get('url').__eq__(add_book_url) and requ.get('method').__eq__("POST"):
            print(requ.get('postData'))
            post_data_list.append(json.loads(requ.get('postData')))
        
        #取消收藏时触发
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
        
        match = re.match(f'{bookmark_event_url}.*',requ.get('url'))
        if not match == None:
            tempdict = {'url':requ.get('url')}
            post_data_list.append(tempdict)


    print(f'analysis: loglen:{log.__len__()}\tparams_none:{params_none}\trequ_none:{requ_none}\tpost_list:{post_list.__len__()}')



def delegate_title_is_pixiv(x: WebDriver):
    '''
    等待用户自行跳转至主页 按照步长执行委托
    处理从浏览器截取的log数据
    '''
    log = []
    log = x.get_log('performance')
    analysis_log(log,post_list)

    title = x.title
    return 'pixiv'.__eq__(title)


def open_discovery():

    od_dict = custom_driver.get_custom_options_desired_capabilities(config.get_browser(), config.get_is_proxies, True)
    driver = custom_driver.get_custom_driver(name=config.get_browser(),options=od_dict.get('options'),desired_capabilities=od_dict.get('desired_capabilities'))
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
    
    # log = driver.get_log('performance')
    # for item in log:
    #     message = json.loads(item.get('message'))
    #     item['message'] = message
    # downloads.save_str_data(config.performance_log_path,json.dumps(log))

    driver.quit()


if __name__ == '__main__':
    bookmark_event_url2 = 'https://event.pixiv-recommend.net/?platform=pc&action=click-bookmark'
    sample1 = "https://event.pixiv-recommend.net/?platform=pc&action=click-bookmark&zone=discovery&method=clustering_bqalgc&illust_id=92834061&seed_illust_ids=90553117%2C93470454%2C93623887%2C93790321&login=yes&user_id=25832134&p_ab_id=2&p_ab_id_2=8&p_ab_d_id=773787977"
    sample2 = 'https://event.pixiv-recommend.net/?platform=pc&action=click-bookmark&zone=discovery&method=clustering_bqalgc&illust_id=91975962&seed_illust_ids=86075831%2C91123048%2C91766083%2C93623887%2C93686296%2C93790321&login=yes&user_id=25832134&p_ab_id=0&p_ab_id_2=2&p_ab_d_id=320056489'
    match = re.match('https://event.pixiv-recommend.net/\?platform=pc&action=click-bookmark.*',sample1)
    print(match.group())
    # open_discovery()
    # downloads.save_str_data(config.bookmarkdata_path,json.dumps(post_list))
    print('开始执行下载')