#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author : 艾登Aiden
# @Email : aidenlen@163.com
# @Date : 2021-07-17 16:57:03
# @FilePath : \undefinedc:\Users\Administrator\Desktop\main.py
import httpx
import parsel
import json
import re
from os import makedirs
from os.path import exists
from selenium import webdriver
from selenium.webdriver import ChromeOptions

# 目标url
URL = input('******网页持久化下载器v1.0******\n****** Author: Aiden艾登 ****** \n请输入url:')

# 输入文件名
input_text = input('请输入文件名:')
FILENAME = input_text + '/' + input_text + '.html'

# IMG_URLS 容器单项存放 [图片后缀, img标签, 对应链接, 本地路径, 计数]
IMG_URLS = []

# 默认文件与文件夹同名
RESULTS_DIR = input_text
# 判定文件夹是否存在, 不在则新建
exists(RESULTS_DIR) or makedirs(RESULTS_DIR)


# 浏览器设置
option = ChromeOptions()
# 无头模式
option.add_argument('--headless')
browser = webdriver.Chrome(options=option)
# 隐藏webdriver属性
browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
})


def scrape(url):
    try:
        response = httpx.get(url)
        if response.status_code == 200:
            return response
    except Exception as e:
        print(e)

def scrape_index():
    print("scraping url: ", URL)
    browser.get(URL)
    browser.implicitly_wait(10)
    return browser.page_source

def parse_img(text):
    """提取img标签
    param: Request 对象
    return: 
    """
    # 默认
    # res.encoding = 'utf-8'
    selector = parsel.Selector(text)
    imgs = selector.xpath('//img').getall()
    # print(len(imgs))
    # print(imgs)

    items = []
    # clean_links 用于剔除的列表 
    clean_links = []
    img_last = ['jpg','jpeg', 'png','gif','PSD', 'Bmp', 'Tiff', 'Webp']
    for img in imgs:
        pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        link = re.compile(pattern).findall(img)
        if link:
            # print(link[0])
            # 本地路径
            for index in range(len(img_last)):
                # 比较图片后缀
                if link[0][-3:] == img_last[index] or link[0][-4:] == img_last[index]:
                    items.append([img_last[index], img, link[0]])
                    clean_links.append(link[0])
    
    # 去重
    clean_links = list(set(clean_links))
    # print(clean_links)
    # print(len(clean_links))
    # print(items)
    count = 1
    for item in items:
        if item[-1] in clean_links:
            # 添加计数count 和 本地路径 localpath
            localpath = '{}.{}'.format(count, item[0])
            item.append(localpath)
            item.append(count)
            IMG_URLS.append(item)
            count += 1      
    return

def save_images(url, name):
    res = scrape(url)
    image_name = RESULTS_DIR + '/' + name
    with open(image_name, 'wb') as file:
        file.write(res.content)
    print('已保存图片: ', image_name)

def replace_local(text):
    text0 = text
    for img_url in IMG_URLS:
        new_img = '<img src="{}"/>'.format(img_url[2])
        text0 = text0.replace(img_url[1], new_img)
    return text0

def save_text(text):
    with open(FILENAME, 'w', encoding='utf-8') as file:
        file.write(text)
    print('已保存文件: ', FILENAME)

def main():
    text = scrape_index()
    parse_img(text)
    # print(IMG_URLS)
    # print(len(IMG_URLS))
    '''
    IMG_URL=[
    'png', 
    '<img class="rich_pages" data-ratio="1.2952127659574468" data-s="300,640" data-src="https://mmbiz.qpic.cn/mmbiz_png/DAE6TYB3GWica1nT2wbEM4icI9COMmjZBtPw46LnHibgf9N3WEpRxbDzD9Vh0M1AlXoA56osxuZ2l7ia1gQPTX1bGA/640?wx_fmt=png" data-type="png" data-w="1128" style="height: 271px;width: 209px;overflow-wrap: break-word !important;" _width="209px">', 
    'https://mmbiz.qpic.cn/mmbiz_png/DAE6TYB3GWica1nT2wbEM4icI9COMmjZBtPw46LnHibgf9N3WEpRxbDzD9Vh0M1AlXoA56osxuZ2l7ia1gQPTX1bGA/640?wx_fmt=png', 
    '14.png', 
    14
    ]
    '''
    for img_url in IMG_URLS:
        save_images(img_url[2], img_url[3])
    new_text = replace_local(text)
    save_text(new_text)
    print("Task Done!")


if __name__ == '__main__':
    main()