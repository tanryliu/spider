import requests
import os
import string
import threading
import random, time
import re
from bs4 import BeautifulSoup

host = 'https://hh.flexui.win/'

headers={
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    'Referer':host,
}


class myThred(threading.Thread):
    def __init__(self,url,dir,filename):
        threading.Thread.__init__(self)
        self.ThreadID = filename
        self.url = url
        self.dir = dir
        self.filename = filename

    def run(self):
        download_pic(self.url,self.dir,self.filename)

def download_pic(url,dir,filename):
    try:
        req = requests.get(url, headers=headers)
        if req.status_code == 200:
            with open(str(dir) + '/' + str(filename) + '.jpg', 'wb+') as f:
                f.write(req.content)
        else:
            print("发生错误，跳过下载....." + str(req.status_code))
    except (TimeoutError,ConnectionError,requests.exceptions.ConnectionError,requests.exceptions.ProxyError) as e:
        print("链接超时: " + str(e))

def open_url(url):
    try:
        req = requests.get(url,headers=headers)
        req.encoding = 'GBK'
        return req
    except (TimeoutError,ConnectionError,requests.exceptions.ConnectionError,requests.exceptions.ProxyError) as e:
        print('链接超时' + str(e))

def get_page(url):
    url_list = []
    html = open_url(url)
    soup = BeautifulSoup(html.text,'lxml')
    article_url = soup.select('tbody > tr > td.tal > h3 > a')
    for url in article_url:
        if 'green' in str(url):
            url = str(host) + url.get('href')
            url_list.append(url)
    return url_list

def get_article(url):
    global times
    times=times+1
    print('准备下载第'+ str(times) +'个主题图片')
    img_all =[]
    html = open_url(url)
    soup = BeautifulSoup(html.text,'lxml')
    
    post = soup.select('div.tipad')[1]
    post = post.get_text()
    rulePosted ='Posted:(.+?) \d\d\:\d\d \| '
    ruleDate='Posted:(.+?)-\d\d \d\d\:\d\d \| '
    posted=re.findall(rulePosted, post)
    Date=re.findall(ruleDate, post)
    Date=Date[0]

    title = soup.select('td > h4')[0]
    title = '['+posted[0]+']'+title.get_text()
    pattern=r'[\\/:*?"<>|\r\n]+'
    title= re.sub(pattern, " ", title)
    
    img_urls = soup.select('div.tpc_content.do_not_catch > input')
    if len(img_urls) ==0 :
        img_urls = soup.find_all('input')
    for img_url in img_urls:
        img_url = img_url.get('data-src')
        if str(img_url) != 'None':
            img_all.append(img_url)
    img_sum = len(img_all)
    print('当前帖子：\n' + str(title) + '\n共计取到 ' + str(img_sum) + ' 张图片连接......')

    if img_sum < 3:
    	print('当前帖子图片数量少于3张，跳过下载')
    else:
	    filePath=Date+'\\'
	    if os.path.exists(filePath) == False:
	        os.makedirs(filePath)
	    if os.path.exists(filePath+title) == False:
	        os.makedirs(filePath+title)
	        filename = 1
	        threads = []
	        for imgurl in img_all:
	            thread = myThred(imgurl,filePath+title,filename)
	            thread.start()
	            threads.append(thread)
	            filename += 1
	        for t in threads:
	            t.join()
	        timer = random.randint(2,5)
	        print('下载完成............\n' + '休眠 ' + str(timer) + ' 秒......')
	        time.sleep(timer)
	    else:
	        print("文件夹已存在，跳过下载。")


	        
i = 1
times = 0
while i <= 100:
    page_url = 'https://hh.flexui.win/thread0806.php?fid=16&search=&page=' + str(i)
    try:
        print('正在下载第'+ str(i) +  '页内容.')
        pagelist = get_page(page_url)
        for url in pagelist:
        	get_article(url)
    except (IndexError,TimeoutError)as e:
        print('发生错误....跳过下载......' + str(e))
    i += 1
