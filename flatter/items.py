# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import json

import scrapy
from itemloaders.processors import MapCompose, Join, TakeFirst, Identity, Compose
from w3lib.html import remove_tags
from unicodedata import normalize
from functools import partial
from utilites.item_select_handlers import *
from utilites.date_normalizer import date_normalize

normalize_nfkd = partial(normalize, 'NFKD')


class FlatPaginationItem(scrapy.Item):
    source = scrapy.Field()
    url = scrapy.Field()
    date_last_view = scrapy.Field()
    need_parse = scrapy.Field()
    info = scrapy.Field()
    date_change_sign = scrapy.Field()
    date_added = scrapy.Field()


class FlatParser(scrapy.Item):
    uid = scrapy.Field(
        input_processor=Compose(select_first, remove_tags, str.strip, normalize_nfkd, select_uid),
        output_processor=TakeFirst(),
    )
    uid_base64 = scrapy.Field()
    source = scrapy.Field()
    url = scrapy.Field()
    url_base64 = scrapy.Field()
    contract_type = scrapy.Field()
    description = scrapy.Field(
        input_processor=MapCompose(remove_tags, str.strip),
        output_processor=Join(),
    )
    country = scrapy.Field()
    region = scrapy.Field()
    city = scrapy.Field()
    district = scrapy.Field()
    address = scrapy.Field()
    lat_degrees = scrapy.Field()
    lon_degrees = scrapy.Field()
    realty_type = scrapy.Field()
    area = scrapy.Field(
        input_processor=Compose(select_first, remove_tags, str.strip, normalize_nfkd, select_area),
        output_processor=TakeFirst(),
    )
    price = scrapy.Field()

    metr_price = scrapy.Field()
    room_count = scrapy.Field(
        input_processor=Compose(select_first, remove_tags, str.strip, normalize_nfkd, select_room_count),
        output_processor=TakeFirst(),
    )
    floor = scrapy.Field(
        input_processor=Compose(select_first, remove_tags, str.strip, normalize_nfkd, select_floor),
        output_processor=TakeFirst(),
    )
    number_of_storeys = scrapy.Field(
        input_processor=Compose(select_first, remove_tags, str.strip, normalize_nfkd, select_num_stor),
        output_processor=TakeFirst(),
    )
    year_of_construction = scrapy.Field(
        input_processor=Compose(select_first, remove_tags, str.strip, normalize_nfkd, select_year),
        output_processor=TakeFirst(),
    )
    material_wall = scrapy.Field(
        input_processor=Compose(select_first, remove_tags, str.strip, normalize_nfkd, select_material),
        output_processor=TakeFirst(),
    )
    finish_condition = scrapy.Field(
        input_processor=Compose(select_first, remove_tags, str.strip, normalize_nfkd, select_finish),
        output_processor=TakeFirst(),
    )
    parking = scrapy.Field(
        input_processor=Compose(select_first, remove_tags, str.strip, normalize_nfkd, select_parking),
        output_processor=TakeFirst(),
    )
    owner_name = scrapy.Field()
    owner_phone = scrapy.Field()
    owner_email = scrapy.Field()
    photos = scrapy.Field(
        input_processor=Compose(lambda v: '{' + ' ,'.join([k for k in v]) + '}')
    )
    created_at = scrapy.Field(
        input_processor=Compose(select_first, remove_tags, str.strip, normalize_nfkd, date_normalize)
    )
    updated_at = scrapy.Field()
    date_parse = scrapy.Field()
    close_at = scrapy.Field()
    days_of_life = scrapy.Field()
    html_src = scrapy.Field()
