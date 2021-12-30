from .items import FlatPaginationItem, FlatParser
from utilites.proxy_cheker import is_bad_proxy
from utilites.db import PostgreSQL


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
            item['updated_at'] = item['created_at']
            id_rec = self.db.get_id_from_flat_parser('url_base64', item['url_base64'])
            if id_rec:
                self.db.update_item('flat_parser', item, 'id_rec', id_rec)
            else:
                self.db.insert_item('flat_parser', item)

            id_pagination = self.db.get_id_from_flat_pagination('url', item['url'])
            item_pagination = dict()
            item_pagination['source'] = item['source']
            item_pagination['url'] = item['url']
            item_pagination['date_last_view'] = item['date_parse']
            item_pagination['need_parse'] = 'false'
            item_pagination['info'] = 'new'
            item_pagination['date_change_sign'] = item['date_parse']
            item_pagination['date_added'] = item['created_at']
            if id_pagination:
                self.db.update_item('flat_pagination', item_pagination, 'id', id_pagination)
            else:
                self.db.insert_item('flat_pagination', item_pagination)
        return ''

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
