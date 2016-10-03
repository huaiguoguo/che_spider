import time
from guazi_spider import db
import json


class HtmlOutper(object):
    def __init__(self):
        self.datas = {}
        self.db = db.DB('localhost', 3306, 'root', '111111', 'guaziche', 'UTF8')

    def collect_data(self, data):
        print('搜集数据并且赋值')
        if data is None:
            return
        self.datas = data

    # 把所有的品牌和车系写入 brands表和cars表
    def write_brands_cars(self):
        print('准备sql语句')
        brand_sql = "INSERT INTO brands (`brand_name`, `pinyin`, `url`, `data-gzlog`, `title`, `created_at`) " \
                    "VALUES(%s, %s, %s, %s, %s, %s); "
        cars_sql = "INSERT INTO cars (`cars_name`, `url`, `data-gzlog`, `title`, `created_at`, `brand_id`) " \
                   "VALUES(%s, %s, %s, %s, %s,  %s); "
        brands = self.datas
        print('准备循环拼音')
        for pinyin in brands:
            print('循环拼音【%s】里面的品牌', pinyin)
            for brand in brands[pinyin]:
                print("开始循环写入拼音【%s】里面的品牌:【%s】", pinyin, brand['brand_name'])
                lastrowid = self.db.execute(brand_sql, (
                    brand['brand_name'],
                    pinyin, brand['href'],
                    brand['data_gzlog'],
                    brand['title'],
                    int(time.time())
                ))
                id = lastrowid

                print("准备循环写入拼音【%s】里面的品牌:【%s】【%d】里面的车系", pinyin, brand['brand_name'], id)
                for car in brand['cars']:
                    print("开始循环写入拼音【%s】里面的品牌:【%s】【%d】下面的车系:%s", pinyin, brand['brand_name'], id, car['cars_name'])
                    self.db.execute(cars_sql, (
                        car['cars_name'],
                        car['href'],
                        car['data_gzlog'],
                        car['title'],
                        int(time.time()),
                        id
                    ))
                    print("车系[%s]写入完成", car['cars_name'])
                print("拼音【%s】里面的品牌:【%s】【%d】里面的车系写入完成", pinyin, brand['brand_name'], id)
            print("拼音【%s】写入完成", pinyin)

    # 把车辆简要信息写入cars_info表里面
    def write_cars_info(self):
        car_info_sql = "INSERT INTO car_info (`cars_id`, " \
                       "`url`, `img_url`, `title`, `present_price`, " \
                       "`original_price`, `city`, `registration_date`, `mileage`, `created_at`) " \
                       "VALUES(%s, %s, %s, %s, %s,  %s, %s, %s,  %s, %s); "

        print('开始循环html_output.datas中的数据并且写入cars_info')
        for cars in self.datas:
            print(cars['cars_id'], cars['title'], cars['url'], cars['mileage'], "<br>")
            lastrowid = self.db.execute(car_info_sql, (
                cars['cars_id'],
                cars['url'],
                cars['img_url'],
                cars['title'],
                cars['present_price'][:-1],
                cars['original_price'][:-1],
                cars['city'],
                cars['registration_date'],
                cars['mileage'][2:-3],
                int(time.time())
            ))
            print('cars_info.id:%d' % lastrowid)

    def write_cars_info_detail(self, id):
        print("开始更新id:%s记录的详细信息"% id)
        detail = str(self.datas)
        # print(type(detail))
        # print(detail)
        car_sql = "UPDATE car_info set detail=%s , updated_at=%s WHERE id = %s"
        self.db.execute(car_sql, (detail, int(time.time()), id))
        # print(self.db.cur)
        print("详细信息更新完毕")
        print('+++++++++++++++++++++++++++++++++++++++')
