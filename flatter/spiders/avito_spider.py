from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
from base64 import b64encode
from scrapy.loader import ItemLoader
from ..items import FlatParser
from itemloaders.processors import TakeFirst, MapCompose


class AvitoSpider(CrawlSpider):
    name = 'avito_spider'
    allowed_domains = ['www.avito.ru']
    start_urls = []
    rules = (
        Rule(
            LinkExtractor(
                allow='.*/kvartiry/.*',
                restrict_xpaths='//a[@itemprop="url"]'
            ),
            callback='handle_flat_page',
            follow=True
        ),
        Rule(
            LinkExtractor(
                allow='.*/kvartiry/prodam-.*/?p=\d+',
                restrict_xpaths="//div[contains(@class, 'pagination-pages')]"
            ),
            follow=True
        ),
    )

    def __init__(self, region='moskva', **kwargs):
        regions = region.split()
        for item in regions:
            self.start_urls.append(f"https://www.avito.ru/{item}/kvartiry/prodam")
        super().__init__(**kwargs)

    def handle_flat_page(self, response):
        content = response.xpath('//div[@class="item-view-content"]')
        uid = response.xpath('//span[@data-marker="item-view/item-id"]/text()').get()
        uid_base64 = b64encode(uid.encode()).decode()
        region = response.xpath('//select[@id="region"]/option[@selected]/text()').get()
        if content:
            loader = ItemLoader(item=FlatParser(), response=response, selector=content)
            loader.default_output_processor = TakeFirst()
            loader.default_input_processor = MapCompose(str.strip)
            url = response.url
            loader.add_value('uid', uid)
            loader.add_value('uid_base64', uid_base64)
            loader.add_value('source', 'avito_ru')
            loader.add_value('url', url)
            loader.add_value('url_base64', b64encode(url.encode()).decode())
            loader.add_value('contract_type', 'Продажа')
            loader.add_xpath('description', '//div[@itemprop="description"]')
            loader.add_value('country', 'Россия')
            loader.add_value('region', region)
            loader.add_xpath('city', '//span[@itemprop="name"]/text()')
            loader.add_xpath('district', '//span[@class="item-address-georeferences-item__content"]/text()')
            loader.add_xpath('address', '//span[@class="item-address__string"]/text()')
            loader.add_xpath('lat_degrees', '//div[contains(@class, "item-map-wrapper")]/@data-map-lat')
            loader.add_xpath('lon_degrees', '//div[contains(@class, "item-map-wrapper")]/@data-map-lon')
            loader.add_xpath('area', '//ul[@class="item-params-list"]/li[@class="item-params-list-item"][./span[contains(text(), "Общая площадь:")]]')
            loader.add_xpath('price', '//span[@itemprop="price"]/@content')
            loader.add_xpath('room_count', '//ul[@class="item-params-list"]/li[@class="item-params-list-item"][./span[contains(text(), "Количество комнат:")]]')
            loader.add_xpath('floor', '//ul[@class="item-params-list"]/li[@class="item-params-list-item"][./span[contains(text(), "Этаж: ")]]')
            loader.add_xpath('year_of_construction', '//ul[@class="item-params-list"]/li[@class="item-params-list-item"][./span[contains(text(), "Год постройки:")]]')
            loader.add_xpath('material_wall', '//ul[@class="item-params-list"]/li[@class="item-params-list-item"][./span[contains(text(), "Тип дома:")]]')
            loader.add_xpath('finish_condition', '//ul[@class="item-params-list"]/li[@class="item-params-list-item"][./span[contains(text(), "Ремонт:")]]')
            loader.add_value('realty_type', 'Квартира')
            loader.add_xpath('number_of_storeys', '//ul[@class="item-params-list"]/li[@class="item-params-list-item"][./span[contains(text(), "Этаж: ")]]')
            loader.add_xpath('owner_name', '//div[@data-marker="seller-info/name"]/a/text()')
            loader.add_xpath('parking', '//ul[@class="item-params-list"]/li[@class="item-params-list-item"][./span[contains(text(), "Парковка:")]]')
            loader.add_xpath('photos', '//div[contains(@class, "gallery-extended-img-frame")]/@data-url')
            loader.add_xpath('created_at', '//div[@class="title-info-metadata-item-redesign"]/text()')
            loader.add_value('date_parse', datetime.now().isoformat())
            yield loader.load_item()
