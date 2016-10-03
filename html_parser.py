from bs4 import BeautifulSoup
import re
import urllib.parse
from guazi_spider import html_downloader
from guazi_spider import html_parser


class HtmlParser(object):
    def __init__(self):
        self.downloader = html_downloader.HtmlDownloader()

    def _get_new_urls(self, url, soup):
        new_urls = set()
        links = soup.find_all('a', href=re.compile(r"/view/\d+\.htm"))

        for link in links:
            new_url = link['href']
            new_full_url = urllib.parse.urljoin(url, new_url)
            new_urls.add(new_full_url)
        return new_urls

    def _get_new_data(self, soup):
        li_data = soup.find('ul', attrs={'class': 'o-b-list'}).find_all('li')
        link_dirct = {}
        for li in li_data:
            pinyin = li.find('span').get_text()
            links = li.find('div').find_all('a')
            brands = []
            for link in links:
                data_gzlog = link.get('data-gzlog').strip()
                href = link.get('href').strip()
                title = link.get('title').strip()
                brand = link.get_text().strip()

                # 查出某个品牌下面的所有车系, 然后加入品牌下面
                cars = self.getCars(href)

                # 某个字母下面的所有品牌
                brand = {'data_gzlog': data_gzlog, 'href': href, 'title': title, 'brand_name': brand, 'cars': cars};
                print(brand)
                brands.append(brand)

            # 把某个字母下的所有品牌 添加到 对应的字母当中
            link_dirct[pinyin] = brands
        return link_dirct

    def getCars(self, href):
        cars_url = urllib.parse.urljoin("http://www.guazi.com/", href)
        html_string = self.downloader.download(cars_url)
        cars_data = []

        cars_soup = BeautifulSoup(html_string, 'html.parser', from_encoding='utf-8')
        cars = cars_soup.find("dd", attrs={'class': 'clickTagWidget'}).find_all('a')
        for car in cars:
            data_gzlog = car.get('data-gzlog').strip()
            href = car.get('href').strip()
            title = car.get('title')
            cars_name = car.get_text().strip()
            cars_data.append({'data_gzlog': data_gzlog, 'href': href, 'title': title, 'cars_name': cars_name})
        return cars_data

    def parse(self, html_string):
        if html_string is None:
            return None

        soup = BeautifulSoup(html_string, 'html.parser', from_encoding='utf-8')
        # new_urls = self._get_new_urls(soup)
        new_data = self._get_new_data(soup)
        return new_data

    # 分析 每一页 上面的单个车辆的简要信息
    def make_single_cars(self, cars_box, cars_id):
        # a链接
        a_link = cars_box.find('a', attrs={'class': 'imgtype'}).get('href')
        # 图片链接
        img_link = cars_box.find('img').get('src')
        # 标题链接
        title = cars_box.find('p', attrs={'class': 'infoBox'}).find('a').get_text()
        # 上牌时间和行驶里程
        title_2 = cars_box.find('p', attrs={'class': 'fc-gray'}).find_all('span')
        # 城市
        city = title_2[0].get_text().strip()
        # 上牌时间
        registration_date = title_2[1].get_text().strip()
        # 行驶里程
        if cars_box.find('p', attrs={'class': 'fc-gray'}).find('em'):
            travel_mileage = cars_box.find('p', attrs={'class': 'fc-gray'}).get_text().split('|')[1].strip()
        else:
            travel_mileage = cars_box.find('p', attrs={'class': 'fc-gray'}).get_text().split('上牌')[1].strip()

        # 价格
        title_3 = cars_box.find('p', attrs={'class': 'priType-s'})
        present_price = title_3.find('span').find('i').get_text().strip()  # 现价
        original_price = ''
        if title_3.find('s') is not None:
            original_price = title_3.find('s').get_text().strip()  # 原价
        return {'url': a_link, 'img_url': img_link, 'img_url': img_link, 'title': title, 'city': city,
                'registration_date': registration_date, 'mileage': travel_mileage,
                'present_price': present_price, 'original_price': original_price, 'cars_id': cars_id}

    # 获得车辆简要信息
    def _get_cars_data(self, soup, cars_id):
        print('开始取本页所有车辆信息')
        cars_boxs = soup.find_all('div', attrs={'class': 'list-infoBox'})
        cars_data = []
        count = 1
        for cars_box in cars_boxs:
            print('开始取本页第一辆车:%d' % count)
            cars_data.append(self.make_single_cars(cars_box, cars_id))
            count = count + 1
        return cars_data

    def parse_cars_info(self, html_string, cars_id):
        if html_string is None:
            return None
        soup = BeautifulSoup(html_string, 'html.parser', from_encoding='utf-8')
        new_data = self._get_cars_data(soup, cars_id)
        print('返回本页的车辆信息')
        return new_data

    # 下载某个车辆的详情信息, 并且解析成为soup
    def ParseCarDetail(self, detail_page):
        print("开始下载并分析 %s" % detail_page)
        html_string = self.downloader.download(detail_page)
        soup = BeautifulSoup(html_string, 'html.parser', from_encoding='utf-8')
        data = self.getCarsInfoDetail(soup)
        print("分析完毕")
        return data

    def getCarsInfoDetail(self, soup):
        detail_dirct = {}
        # 图片组件
        car_slideshow = soup.find('div', attrs={'class': 'det-sumleft slideshow'})
        if car_slideshow:
            detail_dirct['car_slideshow'] = self.car_slideshow(car_slideshow)

        # 车辆概要信息
        car_appoint = soup.find('div', attrs={'class': 'det-sumright appoint'})
        if car_appoint:
            detail_dirct['car_appoint'] = self.car_appoint(car_appoint)

        # 检测结果信息
        car_check_result = soup.find('div', attrs={'class': 'detect-bd clearfix'})
        if car_check_result:
            detail_dirct['car_check_result'] = self.car_check_result(car_check_result)

        # 车源基本信息
        car_base = soup.find('div', attrs={'class': 'modbox', 'id': 'base'})
        if car_base:
            detail_dirct['car_base'] = self.car_base(car_base)

        # 车辆图片
        car_picture = soup.find('div', attrs={'class': 'modbox', 'id': 'picture'})
        if car_picture:
            detail_dirct['car_picture'] = self.car_picture(car_picture)

        # 车辆检测报告
        car_report = soup.find('div', attrs={'class': 'modbox1 combox', 'id': 'report'})
        if car_report:
            detail_dirct['car_report'] = self.car_report(car_report)

        # 车辆配置参数
        car_config = soup.find('div', attrs={'class': 'modbox', 'id': 'config'})
        if car_config:
            detail_dirct['car_config'] = self.car_config(car_config)

        return detail_dirct

    # 图片组件分析
    def car_slideshow(self, soup):
        img_list = []
        ul_list = soup.find_all("ul", attrs={'class': 'dt-thumb-img clearfix'})
        for ul in ul_list:
            lis = ul.find_all('li')
            for li in lis:
                img = li.find('img').get('src').split('.jpg')[0] + '.jpg'
                img_list.append(img)
        return img_list

    # 车辆概要信息分析
    def car_appoint(self, soup):
        appoint = {}
        appoint['title'] = soup.find("h1").get_text()
        appoint['car_number'] = soup.find("div", attrs={'class': 'dt-titleinfo clearfix'}).find_all('span')[
            1].get_text()
        appoint['price_1'] = soup.find("b", attrs={'class': 'f30 numtype'}).get_text()
        if soup.find("span", attrs={'class': 'f14'}):
            price = soup.find("span", attrs={'class': 'f14'}).find_all('font')
            appoint['price_2'] = price[0].get_text()
            appoint['price_3'] = price[1].get_text()
            appoint['service_charge'] = soup.find('div', attrs={'class': 'car-fuwu'}).find('span').get_text()

        assort = soup.find('ul', attrs={'class': 'assort clearfix'}).find_all('li')
        appoint['gearbox'] = assort[2].get_text()
        appoint['emission'] = assort[3].find('b').get_text()
        return appoint

    # 检测结果信息分析
    def car_check_result(self, soup):
        check_result = {}
        check_options = {}
        check_result['check_content'] = soup.find('div', attrs={'class': 'detect-txt'}).get_text()

        # 检测大项[4项]
        options_soup = soup.find('div', attrs={'class': 'detect-xm-c showItem'}).find_all('dl')

        for option_dl in options_soup:
            dds = option_dl.find_all('dd')
            options = {}
            for dd in dds:
                spans = dd.find_all('span')
                if spans[1].find('em') is None:
                    option_val = 1
                else:
                    defects = spans[1].find('ul', attrs={'class': 'fc-9'}).find_all('li')
                    d = []
                    for defect in defects:
                        d.append(defect.get_text().strip())
                    option_val = d
                options[spans[0].get_text().strip()] = option_val
            check_options[option_dl.find('dt').get_text()] = options
        check_result['check_options'] = check_options
        return check_result

    # 车源基本信息分析
    def car_base(self, soup):
        base_dict = {}
        base_info = {}
        base_info_li = soup.find('ul', attrs={'class': 'owner-infor clearfix'}).find_all('li')

        owner = base_info_li[0].get_text().split('\n')
        del owner[0]
        del owner[0]
        owner_list = []
        for o in owner:
            owner_list.append(o.strip().replace('|', ''))
        base_info['owner'] = owner_list

        nianjian = base_info_li[1].get_text()
        base_info['nianjian'] = nianjian.split('：')[1]

        qiangxian = base_info_li[2].get_text()
        base_info['qiangxian'] = qiangxian.split('：')[1]

        shangye_xian = base_info_li[3].get_text()
        base_info['shangye_xian'] = shangye_xian.split('：')[1]

        guohu = base_info_li[4].get_text()
        base_info['guohu'] = guohu.split('：')[1]
        base_info['decription'] = soup.find('p', attrs={'class': 'f-type03'}).get_text()
        return base_info

    # 车辆图片分析
    def car_picture(self, soup):
        img_dict = []
        img_list = soup.find_all('img')
        for img in img_list:
            img_dict.append(img.get('data-original'))
        return img_dict

    # 车辆检测报告分析
    def car_report(self, soup):
        report_dict = {}
        report_title = soup.find_all('div', attrs={'class': 'headline-bd'})
        report_content = soup.find_all('div', attrs={'class': 'detectBox clearfix'})

        report_dict['AccidentInvest'] = self.AccidentInvest(report_title[0], report_content[0])
        report_dict['ExterInterInspection'] = self.ExteriorInteriorInspection(report_title[1], report_content[1])
        report_dict['SystemEquipmentDetection'] = self.SystemEquipmentDetection(report_title[2], report_content[2])
        report_dict['DrivingTest'] = self.DrivingTest(report_title[3], report_content[3])
        # print(report_dict['ExterInterInspection'])
        # print(report_dict['ExterInterInspection']['outer_ins'])
        return report_dict

    # 事故排查
    def AccidentInvest(self, report_title, report_content):
        accident_dict = {}
        content_dict = {}
        table_one = []
        table_two = []
        table_three = []

        content_dict['img'] = report_content.find('img').get('src')
        table = report_content.find_all('table')
        # 第一个table
        table_trs_1 = table[0].find_all('tr')
        for tr in table_trs_1:
            if tr.find_all('td'):
                key1 = tr.find_all('td')[0].get_text()
                value1 = tr.find_all('td')[1].find('i').get('class')[0]
                key2 = tr.find_all('td')[2].get_text()
                value2 = tr.find_all('td')[3].find('i').get('class')[0]
                table_one.append({key1: value1})
                table_one.append({key2: value2})

        # 第二个table
        table_trs_2 = table[1].find_all('tr')
        for tr in table_trs_2:
            if tr.find_all('td'):
                key_1 = tr.find_all('td')[1].get_text()
                value_1 = tr.find_all('td')[2].find('i').get('class')[0]
                key_2 = tr.find_all('td')[4].get_text()
                value_2 = tr.find_all('td')[5].find('i').get('class')[0]
                table_two.append({key_1: value_1})
                table_two.append({key_2: value_2})

        # 第三个table
        table_trs_3 = table[2].find_all('tr')
        for tr in table_trs_3:
            if tr.find_all('td'):
                key1 = tr.find_all('td')[0].get_text()
                value1 = tr.find_all('td')[1].find('i').get('class')[0]
                key2 = tr.find_all('td')[2].get_text()
                value2 = tr.find_all('td')[3].find('i').get('class')[0]
                table_three.append({key1: value1})
                table_three.append({key2: value2})

        table = {}
        table['one'] = table_one
        table['two'] = table_two
        table['three'] = table_three

        # content_dict['table'] = table
        accident_dict['title'] = report_title.find('span', attrs={'class': 'f14'}).get_text()
        accident_dict['content'] = table
        return accident_dict

    # 室内外检查
    def ExteriorInteriorInspection(self, report_title, report_content):
        inspection = {}
        outer_ins = {}
        inner_ins = {}
        title = report_title.find('span', attrs={'class': 'f14'}).get_text()
        inspection['description'] = title

        content = report_content.find('div', attrs={'class': 'outward fl'})

        # 外观检测
        outer = content.find('div', attrs={'class': 'caption-bd'})
        # 外观检测项列表
        outer_options_list = outer.find_all('span')
        outer_options = []
        for options in outer_options_list:
            className = options.find('i').get('class')[0]
            optionText = options.get_text()
            outer_options.append({className: optionText})

        # 示意图
        outer_appearance_con = content.find('div', attrs={'class': 'appearance-con clueEvaluate'})
        outer_img = outer_appearance_con.find('img').get('src')
        # 外观缺陷
        outer_detfect = outer_appearance_con.find_all('div', attrs={'class': 'appearance-det'})

        outer_ins['options'] = outer_options
        outer_ins['sketch_img'] = outer_img

        detail = []
        for defect in outer_detfect:
            detail_d = {}
            outer_detfect_num = defect.find('i').get_text()
            outer_detfect_style = defect.find('i').get('style')

            detail_d['outer_detfect_num'] = outer_detfect_num
            detail_d['outer_detfect_style'] = outer_detfect_style

            outer_detfect_showImage = defect.find('div', attrs={'class': 'appear-mat'})
            showImage_block_style = outer_detfect_showImage.get('style')

            detail_d['showImage_block_style'] = showImage_block_style

            showImage_block_detail = outer_detfect_showImage.find('div', attrs={'class': 'appear-ct'})
            showImage_block_detail_p = showImage_block_detail.find('p').get_text()
            showImage_block_detail_pic = outer_detfect_showImage.find('img').get('src')

            detail_d['showImage_block_detail_p'] = showImage_block_detail_p
            detail_d['showImage_block_detail_pic'] = showImage_block_detail_pic

            detail.append(detail_d)
        outer_ins['detail'] = detail

        inspection['outer_ins'] = outer_ins

        # 内饰检测
        inner_content = report_content.find('div', attrs={'class': 'outward fr'})

        inner = inner_content.find('div', attrs={'class': 'exterior-img'})
        # 内饰示意图
        inner_img = inner.find('img').get('src')
        inner_detaili_list = inner.find('div', attrs={'class': 'appearance-det clueEvaluate'})

        inner_ins['inner_img'] = inner_img

        inner_detail = []
        for defect in inner_detaili_list:
            try:
                detail_d = {}
                inner_detfect_num = defect.find('i').get_text()
                inner_detfect_style = defect.find('i').get('style')

                detail_d['inner_detfect_num'] = inner_detfect_num
                detail_d['inner_detfect_style'] = inner_detfect_style

                inner_detfect_showImage = defect.find('div', attrs={'class': 'appear-mat'})
                showImage_block_style = inner_detfect_showImage.get('style')

                detail_d['showImage_block_style'] = showImage_block_style

                showImage_block_detail = inner_detfect_showImage.find('div', attrs={'class': 'appear-ct'})
                showImage_block_detail_p = showImage_block_detail.find('p').get_text()
                showImage_block_detail_pic = inner_detfect_showImage.find('img').get('src')

                detail_d['showImage_block_detail_p'] = showImage_block_detail_p
                detail_d['showImage_block_detail_pic'] = showImage_block_detail_pic

                inner_detail.append(detail_d)
            except Exception as e:
                pass

        inner_ins['detail'] = inner_detail

        inspection['inner_ins'] = inner_ins
        return inspection

    # 系统设备检测
    def SystemEquipmentDetection(self, report_title, report_content):
        title = report_title.find('span', attrs={'class': 'f14'}).get_text()
        bitbox = report_content.find_all('div', attrs={'class': 'bitbox'})
        box_dict = {}
        box_dict['description'] = title
        for box in bitbox:
            box_title = box.find('p').get_text()

            box_tr = box.find_all('tr')
            td_list = []
            for tr in box_tr:
                if tr.find_all('td'):
                    td = tr.find_all('td')
                    key1 = td[0].get_text().strip()
                    if td[1].find('i'):
                        value1 = td[1].find('i').get('class')[0]
                    else:
                        value1 = td[1].get_text().strip()
                    td_list.append({key1: value1})
                    if len(td) > 2:
                        key2 = td[2].get_text().strip()
                        if td[3].find('i'):
                            value2 = td[3].find('i').get('class')[0]
                        else:
                            value2 = td[3].get_text().strip()
                        td_list.append({key2: value2})
            box_dict[box_title] = td_list
        return box_dict

    # 驾驶检测
    def DrivingTest(self, report_title, report_content):
        driving_drct = {}
        driving_drct['description'] = report_title.find_all('span')[1].get_text()
        li_list = report_content.find_all('li')
        for li in li_list:
            p_dict = {}
            title = li.find('h3').get_text()
            p_options = li.find_all('p')
            for p in p_options:
                if p.find('i').get('class'):
                    p_val = p.find('i').get('class')[0]
                else:
                    p_val = p.find('i').get_text()
                key = p.find('span').get_text()
                p_dict[key] = p_val
            driving_drct[title] = p_dict
        # print(driving_drct)
        return driving_drct

    # 车辆配置参数分析
    def car_config(self, soup):
        config_dict = {}
        table_list = soup.find_all('table')
        for table in table_list:
            tr_list = table.find_all('tr')
            table_title = tr_list[0].find('th').get_text()
            del tr_list[0]
            td_dict = []
            for tr in tr_list:
                td = tr.find_all('td')
                td_dict.append({td[0].get_text(): td[1].get_text()})
            config_dict[table_title] = td_dict
        return config_dict
