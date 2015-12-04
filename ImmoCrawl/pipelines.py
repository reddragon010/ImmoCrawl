# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
import re

from scrapy.conf import settings
from scrapy.exceptions import DropItem

from ImmoCrawl.items import PropertyItem

class RefineDataPipeline(object):
    def process_item(self, item, spider):
        self.add_extras(item)

        item['price'] = self.convert_to_float(item['price'])

        item['size'] = self.convert_to_float(item['size'])
        item['location'] = self.refine_location(item['location'])

        self.trim_all_str_fields(item)

        return item

    def trim_all_str_fields(self, item):
        for a in ['link', 'title', 'text', 'location']:
            item[a] = item[a].strip()

    def add_extras(self, item):
        """:type item: PropertyItem"""
        if item['location'].count("kauf") > 0:
            item['extras'].append('buy')
        if item['location'].count("miete") > 0:
            item['extras'].append('rent')

    def convert_to_float(self, value):
        m = re.search("([1-9][0-9.]*[,0-9]*)", value)
        if not m:
            return 0
        v = m.group(0)
        if v:
            v = v.replace('.','').replace(',','.')
            return float(v)
        return 0

    def refine_location(self, location):
        """:type location: str"""
        if location.count("Wien") == 0 and location.count("wien") == 0:
            return location

        m = re.search("(1[0-2][0-9]0)", location)
        if not m or not m.group(0):
            return location

        return "{} Wien".format(m.group(0))

class MongoDBPipeline(object):
    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

    def save(self, item):
        self.collection.update({ "_id": item['_id'] }, dict(item), upsert=True)

    def process_item(self, item, spider):
        for data in item:
            if not data:
                raise DropItem("Missing {0}!".format(data))

        self.save(item)
        return item

