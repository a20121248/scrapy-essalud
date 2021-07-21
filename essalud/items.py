# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class AfiliadoItem(scrapy.Item):
    dni = scrapy.Field()
    name = scrapy.Field()
    insuredType = scrapy.Field()
    code = scrapy.Field()
    insuranceType = scrapy.Field()
    attentionCenter = scrapy.Field()
    dateFrom = scrapy.Field()
    dateTo = scrapy.Field()
    address = scrapy.Field()
    affiliated = scrapy.Field()
    businessName = scrapy.Field()
    pass
