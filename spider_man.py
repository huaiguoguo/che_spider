from guazi_spider import html_downloader
from guazi_spider import html_output
from guazi_spider import html_parser
from guazi_spider import url_manager
from guazi_spider import db
from json import *

from bs4 import BeautifulSoup
import urllib.parse
import time
import random

import threading
import queue
import socket


# 1,把所有车品牌搜下来 循环写入数据库当中  记下品牌链接
# 2,然后再循环读取数据表当中的车品牌   根据车的品牌找出 此品牌下面的所有车系  记下车系链接
# 3,然后循环所有的车系   读出车系下面的车信息，然后写表表当中  【初次写入车辆简要信息】
# 4,然后再循环读出表当中的车俩简要信息 根据 车输链接 抓取  车辆的全面信息  【二次写入车辆信息】

class SpiderMan(object):
    def __init__(self):

        socket.setdefaulttimeout(5)
        self.queue_url = queue.Queue()
        self.queue_text = queue.Queue()

        self.root_url = 'http://www.guazi.com'
        self.db = db.DB('localhost', 3306, 'root', '111111', 'guaziche', 'UTF8')
        self.urls = url_manager.UrlManager()
        self.downloader = html_downloader.HtmlDownloader()
        self.parser = html_parser.HtmlParser()
        self.outputer = html_output.HtmlOutper()

    # 获得所有的品牌和车系分类, 分别写入品牌表和车系表
    def CrawBrandsCars(self):
        url = urllib.parse.urljoin(self.root_url, "/www/buy/")
        html_string = self.downloader.download(url)
        new_data = self.parser.parse(html_string)
        self.outputer.collect_data(new_data)
        self.outputer.write_bras_cars()

    # 抓取所有车系下面的每一页的车辆简要信息, 不获得详情页面信息  此函数要运行超过8小时
    def CrawCarsInfo(self):
        sql = "select * from cars"
        cur = self.db.select(sql)
        for cars in cur:
            html_string = self.downloader.download(urllib.parse.urljoin(self.root_url, cars['url']))
            soup = BeautifulSoup(html_string, 'html.parser', from_encoding='utf-8')
            print(cars['url']);
            try:
                page_num = soup.find('ul', attrs={'class': 'pageLink clearfix'}).find_all('li')
            except Exception as e:
                print(e)
                continue

            page_count = len(page_num)
            if page_count > 7:
                page_count = page_count - 1

            for x in range(page_count):
                num = x + 1
                page_url = urllib.parse.urljoin(self.root_url, cars['url'] + "o%d/" % num)
                print(page_url)
                page_string = self.downloader.download(page_url)
                new_data = self.parser.parse_cars_info(page_string, cars['id'])
                self.outputer.collect_data(new_data)
                self.outputer.write_cars_info()
                time.sleep(6)  # 每隔6秒 爬取一次

    # 获得所有的城市
    def getCity(self):
        url = urllib.parse.urljoin(self.root_url, "/www/buy/")
        html_string = self.downloader.download(url)
        soup = BeautifulSoup(html_string, 'html.parser', from_encoding='utf-8')
        all_city = soup.find('div', attrs={'class': 'all-city'}).find_all('dl')
        citys_sql = "INSERT INTO citys (`pinyin`, `city_name`, `created_at`) " \
                    "VALUES(%s, %s, %s); "
        for cityobj in all_city:
            letter = cityobj.find('dt').get_text()
            citys = cityobj.find_all('a')
            for city in citys:
                self.db.execute(citys_sql, (
                    letter,
                    city.get_text(),
                    int(time.time())
                ))
        print("成功")

    def main_one(self):
        car_one = self.db.select("select id,url from car_info where id>=11431 and id<=20000")
        for car in car_one:
            print(car['url'])
            detail_url = urllib.parse.urljoin(self.root_url, car['url'])
            data = self.parser.ParseCarDetail(detail_url)
            # 将Python dict类型转换成标准Json字符串
            json_string = JSONEncoder().encode(data)
            self.outputer.collect_data(json_string)
            self.outputer.write_cars_info_detail(car['id'])
            time.sleep(6)  # 抓取每一页 间隔5秒

    def main_two(self):
        car_two = self.db.select("select id,url from car_info where id>=20001 and id<=30000")
        for car in car_two:
            print(car['url'])
            detail_url = urllib.parse.urljoin(self.root_url, car['url'])
            data = self.parser.ParseCarDetail(detail_url)
            # 将Python dict类型转换成标准Json字符串
            json_string = JSONEncoder().encode(data)
            self.outputer.collect_data(json_string)
            self.outputer.write_cars_info_detail(car['id'])
            time.sleep(6)  # 抓取每一页 间隔5秒

    def main_three(self):
        car_three = self.db.select("select id,url from car_info where id>=30001 and id<=40000")
        for car in car_three:
            print(car['url'])
            detail_url = urllib.parse.urljoin(self.root_url, car['url'])
            data = self.parser.ParseCarDetail(detail_url)
            # 将Python dict类型转换成标准Json字符串
            json_string = JSONEncoder().encode(data)
            self.outputer.collect_data(json_string)
            self.outputer.write_cars_info_detail(car['id'])
            time.sleep(6)  # 抓取每一页 间隔5秒

    # 获得车辆详情
    def getCarDetail(self):
        threading.Thread(target=self.main_one, name='LoopThread1').start().join()
        threading.Thread(target=self.main_two, name='LoopThread2').start().join()
        threading.Thread(target=self.main_three, name='LoopThread3').start().join()


if __name__ == '__main__':
    obj_spider = SpiderMan()
    # obj_spider.getCity()
    # obj_spider.CrawBrandsCars()
    # obj_spider.CrawCarsInfo()
    obj_spider.getCarDetail()


    # abc = lambda num: [a * 2 for a in range(num)]
    # print(abc(20))
