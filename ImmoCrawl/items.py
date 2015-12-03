# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class PropertyItem(scrapy.Item):
    _id = scrapy.Field()
    link = scrapy.Field()
    title = scrapy.Field()
    text = scrapy.Field()
    location = scrapy.Field()
    price = scrapy.Field()
    size = scrapy.Field()
    extras = scrapy.Field()