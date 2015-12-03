# -*- coding: utf-8 -*-
import scrapy
import hashlib
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector    import Selector

from ImmoCrawl.items import PropertyItem


class CrawlerSpider(CrawlSpider):
    name = 'crawler'
    allowed_domains = [
        'alleskralle.com',
        'immocontract.edireal.com'
    ]
    start_urls = ['http://www.alleskralle.com/immobilien/at?q_loc=wien&sort_by=ad_date']

    rules = (
        Rule(LinkExtractor(allow=r'\/immobilien\/at\?(.*)&page=[0-9]{0,6}'), callback='parse_ak_item', follow=True),
        Rule(LinkExtractor(allow='http:\/\/immocontract.edireal.com\/immocontract\/servlet\/\.state\?.*objektnummer=.*'), callback='parse_edireal_item', follow=True),

    )

    def parse_ak_item(self, response):
        estateLinks	= Selector(response).xpath('//*[@id="searchResult"]/div[1]/div[2]/ul/li/a[@class="anzeigen_link"]')

        for el in estateLinks:
            link = el.xpath('@href').extract()[0]
            facts = el.xpath('*/strong[@class="fact"]/text()').extract()

            item = PropertyItem()
            item["_id"] = hashlib.sha224(link).hexdigest()
            item["title"] = el.xpath('div[2]/p/text()').extract()[0]
            item["link"] = link
            item["location"] = el.xpath('*/span[@class="ad_location"]/text()').extract()[0]

            if len(facts) > 0 :
                item["price"] = facts[0]

            if len(facts) > 1 :
                item["size"] = facts[1]

            yield item

    def parse_edireal_item(self, response):
        dlBox = Selector(response).xpath('//*[@id="main"]/div[1]/div[2]/div[3]/dl')

        item = PropertyItem()
        item["_id"] = hashlib.sha224(response.url).hexdigest()
        item["link"] = response.url
        item["title"] = Selector(response).xpath('//*[@class="obj-view"]/div[@class="name"]/text()').extract()[0]
        item["text"] = Selector(response).xpath('//*[@id="description"]/p').extract()[0]
        item["location"] = dlBox.xpath('dt[text()="Ort:"]/following-sibling::dd[1]/text()').extract()[0]
        item["price"] = dlBox.xpath('dt[text()="Gesamtmiete:"]/following-sibling::dd[1]/text()').extract()[0]

        try:
            item["size"] = dlBox.xpath('dt[starts-with(text(),"Wohnfl")]/following-sibling::dd[1]/text()').extract()[0]
        except:
            item["size"] = dlBox.xpath('dt[starts-with(text(),"Nutzfl")]/following-sibling::dd[1]/text()').extract()[0]

        item["extras"] = ""
        yield item