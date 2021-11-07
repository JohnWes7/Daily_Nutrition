# Daily_Nutrition
###  使用 Edge 或者 谷歌浏览器chrome  火狐浏览器没测 当作不支持  
&nbsp;
># 食用方法
>>## 前提条件  
>> 1. python 环境 （current version Python 3.9.7）
>> 2. selenium (pip install selenium)
>> 3. lxml (pip install lxml)
>> 4. 一个魔法上网的梯子 (自己用的是ssr **没有梯子能稳定连接github?** [梯子广告招租位](https://github.com/JohnWes7/Daily_Nutrition) Config.ini 可以设置是否启用代理以及代理网址和端口 默认是ssr的默认127.0.0.1:1080)
>> 5. Edge(当前: 95.0.1020.40)|Chrome(当前: 95.0.4638.69)|~~FireFox~~
>>#### 如果版本不兼容可以去找对应版本的driver替换文件夹里的同名文件即可 [Edge的driver 点这对照自己的版本下载](https://developer.microsoft.com/zh-cn/microsoft-edge/tools/webdriver/)
>&nbsp;
>>## 1. 全自动发现下载器 运行downloads文件
>> 运行 downloads.py下载pixiv推荐的插画 可在Config.ini 编辑参数（像是抓取多少张 pixiv发现模式 r18|all|save 等） 
>> 第一次运行会需要登录  
>> 登录后会自动保存cookie(在cookie有效期内不需要再次登录)  
>> 登陆完成后当浏览器跳转至pixiv主页时会自动关闭并记录cookie (path='./data/cookies.json')  
>> 获取推荐和下载会在浏览器自动关闭后由控制台提示获取到的所有id 确认后回车下载  
>> 成功下载过的id会被保存进 ./data/downloadrecord.json 设置可以选择是否用此文件排除重复id  
>> ### ***mode = r18 开冲！***
>&nbsp;
>>## 2. 冲-收藏-下载-器 运行 discovery文件
>>#### 相当于本次进行了收藏的项目
>> 运行 discovery 可直接跳转到 [pixiv发现](https://www.pixiv.net/discovery) 页面 如果本地有cookie可以不用再登录自动跳转到[pixiv发现](https://www.pixiv.net/discovery)  
>> 只要没有回到主页面(因为会导致我觉得你好了然后自动关闭) 把涩图都点个爱心加个收藏 ***放开了冲***  
>> ***冲完了*** 程序会在浏览器关闭的时候自动下载所有 **本次** 用户点过爱心的项目  
>> *手动跳转到[pixiv主页面](https://www.pixiv.net/) (可以浏览器拉到最上面按左上角的PIXIV图标进行跳转) 届时浏览器则会自动安全关闭  直接点X退出浏览器**是可以的** 但需要等一小会才会自动下  
>>### ***我好了***
<br/>
<br/>
chrome和edge executable_path说是被弃用(但好像测的还能用)  
所以这两个的driver就在第一级的文件夹内 和download还有discovery同级
<br/>
firefox驱动在driver文件夹内  
<br/>
如有打开没效果 请按照自己的浏览器版本更换driver  
<br/>

TODO: search文件 可以根据填入的标签搜索下载