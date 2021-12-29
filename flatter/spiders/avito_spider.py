import struct
from urllib.parse import urlparse
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
from utilites.date_normalizer import date_normalize
from base64 import b64encode
from scrapy.loader import ItemLoader
from scrapy.shell import inspect_response
from ..items import FlatPaginationItem, FlatParser
from itemloaders.processors import TakeFirst, MapCompose
from scrapy.exceptions import CloseSpider


class AvitoSpider(CrawlSpider):
    name = 'avito_spider'
    allowed_domains = ['www.avito.ru']
    start_urls = []
    rules = (
        # Rule(
        #     LinkExtractor(
        #         allow='.*/kvartiry/prodam-.*/?p=\d+',
        #         restrict_xpaths="//div[contains(@class, 'pagination-pages')]"
        #     ),
        #     callback='handle_pagination',
        #     follow=True
        # ),
        Rule(
            LinkExtractor(
                allow='.*/kvartiry/.*',
                restrict_xpaths='//a[@itemprop="url"]'
            ),
            callback='handle_flat_page',
            follow=True
        ),
    )

    def __init__(self, region='moskva', **kwargs):
        regions = region.split()
        for item in regions:
            self.start_urls.append(f"https://www.avito.ru/{item}/kvartiry/prodam")
        super().__init__(**kwargs)

    def handle_pagination(self, response):
        flat_items = response.xpath('//div[@data-marker="item"]')
        base_url = 'https://' + urlparse(response.url).netloc
        for flat_item in flat_items:
            url = base_url + flat_item.xpath('//a[@data-marker="item-title"]/@href').get()
            item_date = flat_item.xpath('//div[@data-marker="item-date"]/text()').get()
            item = FlatPaginationItem()
            item['url'] = url
            item['date_change_sign'] = date_normalize(item_date)
            item['info'] = 'test'
            item['date_added'] = str(datetime.today())
            item['source'] = self.name
            item['need_parse'] = 'false'
            item['date_last_view'] = str(datetime.today())
            yield item

    def handle_flat_page(self, response):
        content = response.xpath('//div[@class="item-view-content"]')
        uid = response.xpath('//span[@data-marker="item-view/item-id"]/text()').get()
        if content:
            loader = ItemLoader(item=FlatParser(), response=response, selector=content)
            loader.default_output_processor = TakeFirst()
            loader.default_input_processor = MapCompose(str.strip)
            url = response.url
            loader.add_value('uid', uid)
            loader.add_value('source', self.name)
            loader.add_value('url', url)
            loader.add_value('url_base64', b64encode(url.encode()).decode())
            loader.add_value('contract_type', 'Продажа')
            loader.add_xpath('description', '//div[@itemprop="description"]')
            loader.add_value('country', 'Россия')
            loader.add_value('region', 'test')
            loader.add_value('realty_type', 'Квартира')
            loader.add_xpath('city', '//span[@itemprop="name"]/text()')
            loader.add_xpath('district', '//span[@class="item-address-georeferences-item__content"]/text()')
            loader.add_xpath('address', '//span[@class="item-address__string"]/text()')
            loader.add_xpath('area', '//ul[@class="item-params-list"]/li[@class="item-params-list-item"][./span[contains(text(), "Общая площадь:")]]')
            loader.add_xpath('room_count', '//ul[@class="item-params-list"]/li[@class="item-params-list-item"][./span[contains(text(), "Количество комнат:")]]')
            loader.add_xpath('floor', '//ul[@class="item-params-list"]/li[@class="item-params-list-item"][./span[contains(text(), "Этаж: ")]]')
            loader.add_xpath('number_of_storeys', '//ul[@class="item-params-list"]/li[@class="item-params-list-item"][./span[contains(text(), "Этаж: ")]]')
            loader.add_xpath('year_of_construction', '//ul[@class="item-params-list"]/li[@class="item-params-list-item"][./span[contains(text(), "Год постройки:")]]')
            loader.add_xpath('finish_condition', '//ul[@class="item-params-list"]/li[@class="item-params-list-item"][./span[contains(text(), "Ремонт:")]]')
            loader.add_xpath('material_wall', '//ul[@class="item-params-list"]/li[@class="item-params-list-item"][./span[contains(text(), "Тип дома:")]]')
            loader.add_xpath('parking', '//ul[@class="item-params-list"]/li[@class="item-params-list-item"][./span[contains(text(), "Парковка:")]]')
            loader.add_xpath('price', '//span[@itemprop="price"]/@content')
            loader.add_xpath('lat_degrees', '//div[contains(@class, "item-map-wrapper")]/@data-map-lat')
            loader.add_xpath('lon_degrees', '//div[contains(@class, "item-map-wrapper")]/@data-map-lon')
            loader.add_xpath('photos', '//div[contains(@class, "gallery-extended-img-frame")]/@data-url')
            loader.add_xpath('created_at', '//div[@class="title-info-metadata-item-redesign"]/text()')
            loader.add_value('date_parse', datetime.now().isoformat())
            yield loader.load_item()
