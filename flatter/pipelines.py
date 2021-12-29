# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import psycopg2
from .items import FlatPaginationItem, FlatParser
from utilites.proxy_cheker import is_bad_proxy
from utilites.db import PostgreSQL
from psycopg2 import Error


class FlatParserPipeline(object):

    def open_spider(self, spider):
        self.db = PostgreSQL()

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        if isinstance(item, FlatPaginationItem):
            res = self.db.insert_item('flat_pagination', item)
        elif isinstance(item, FlatParser):
            item['metr_price'] = int(float(item['price'])/float(item['area']))
            id_rec = self.db.get_id_from_flat_parser('url_base64', item['url_base64'])
            if id_rec:
                self.db.update_item('flat_parser', item, 'id_rec', id_rec)
            else:
                self.db.insert_item('flat_parser', item)
        return item

class ProxyPickerPipeline(object):

    def open_spider(self, spider):
        self.file = open('proxy_list.txt', 'a')

    def close(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        address = item['ip'] + ':' + item['port']
        if is_bad_proxy(address):
            return f"Прокси адрес {address} - не прошел проверку"
        else:
            print(f"https://{address}", file=self.file)
            return  f"Прокси адрес {address} - добавлен в список"
