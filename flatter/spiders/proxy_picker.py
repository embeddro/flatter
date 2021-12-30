import scrapy


class ProxyPickerSpider(scrapy.Spider):
    name = 'proxy_picker'
    allowed_domains = ['hidemy.name']
    start_urls = ['https://hidemy.name/ru/proxy-list/?type=s']
    custom_settings = {
        'EXTENSIONS': {
                        'scrapy.extensions.closespider.CloseSpider': 500
                       },
        'CLOSESPIDER_TIMEOUT': '15',
        'ITEM_PIPELINES': {
                        'flatter.pipelines.ProxyPickerPipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {},
    }

    def parse(self, response):
        table_block = response.xpath('//div[@class="table_block"]')
        if table_block:
            rows = table_block.xpath('//tbody/tr')
            for row in rows:
                ip = row.xpath('./td[1]/text()').get()
                port = row.xpath('./td[2]/text()').get()
                yield {"ip": ip, "port": port}
        for href in response.xpath("//div[@class='pagination']//li/a/@href").getall():
            yield scrapy.Request(response.urljoin(href), self.parse)
