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
        'immocontract.edireal.com',
        'immowelt.at'
    ]
    start_urls = [
        'http://www.alleskralle.com/immobilien/at?q_loc=wien&q_ty=1&sort_by=ad_date&f[0]=ik_form%3Awohnung',
        'http://www.alleskralle.com/immobilien/at?q_loc=wien&q_ty=2&sort_by=ad_date&f[0]=ik_form%3Awohnung',
    ]

    rules = (
        #Rule(LinkExtractor(deny='.*inaccessibleexpose=1.*')),
        Rule(LinkExtractor(allow=r'http:\/\/www.alleskralle.com\/immobilien\/at\?(.*)&page=[0-9]{0,2}'), callback='parse_ak_item'),
        Rule(LinkExtractor(allow='http:\/\/immocontract\.edireal\.com\/immocontract\/servlet\/\.state\?.*objektnummer=.*'), callback='parse_edireal_item'),
        Rule(LinkExtractor(allow='http:\/\/www\.immowelt\.at\/expose\/.*'), callback='parse_immowelt_item'),
    )

    def parse_ak_item(self, response):
        estateLinks	= Selector(response).xpath('//*[@id="searchResult"]/div[1]/div[2]/ul/li/a[@class="anzeigen_link"]')

        for el in estateLinks:
            link = el.xpath('@href').extract()[0]
            facts = el.xpath('//strong[@class="fact"]/text()').extract()
            yield scrapy.Request(link)

            #item = PropertyItem()
            #id = hashlib.sha224(response.url).hexdigest()
#
            #item["_id"] = "{}_{}".format('ak', id)
            #item["link"] = link
#
            #item["title"] = el.xpath('div[2]/h2/text()').extract()[0]
            #item["location"] = el.xpath('*/span[@class="ad_location"]/text()').extract()[0]
            #item["text"] = " ".join(el.xpath('*/p/text()').extract())
            #if len(facts) > 0 :
            #    item["price"] = facts[0]
#
            #if len(facts) > 1 :
            #    item["size"] = facts[1]
#
            #item["extras"] = []
#
            #yield item

    def parse_edireal_item(self, response):
        dlBox = Selector(response).xpath('//*[@id="main"]/div[1]/div[2]/div[3]/dl')

        item = PropertyItem()
        item["_id"] = hashlib.sha224(response.url).hexdigest()
        item["link"] = response.url

        item["title"] = Selector(response).xpath('//*[@class="obj-view"]/div[@class="name"]/text()').extract()[0]
        item["text"] = Selector(response).xpath('//*[@id="description"]/p').extract()[0]
        item["location"] = dlBox.xpath('dt[text()="Ort:"]/following-sibling::dd[1]/text()').extract()[0]
        try:
            item["price"] = dlBox.xpath('dt[text()="Gesamtmiete:"]/following-sibling::dd[1]/text()').extract()[0]
        except:
            item["price"] = dlBox.xpath('dt[text()="Kaufpreis:"]/following-sibling::dd[1]/text()').extract()[0]

        try:
            item["size"] = dlBox.xpath('dt[starts-with(text(),"Wohnfl")]/following-sibling::dd[1]/text()').extract()[0]
        except:
            item["size"] = dlBox.xpath('dt[starts-with(text(),"Nutzfl")]/following-sibling::dd[1]/text()').extract()[0]

        item["extras"] = []
        yield item

    def parse_immowelt_item(self, response):
        qf = Selector(response).xpath('//*[@class="quickfacts left"]')

        item = PropertyItem()
        item["_id"] = hashlib.sha224(response.url).hexdigest()
        item["link"] = response.url

        item["title"] = qf.xpath('h1/text()').extract()[0]
        item["text"] = " ".join(Selector(response).xpath('//*[@id="divImmobilie"]/*/div[@class="section_content"]/*').extract())
        item["location"] = qf.xpath('//div[starts-with(@class,"location")]/text()').extract()[0]
        item["price"] = qf.xpath('//div[starts-with(@class, "hardfact")]/strong/text()').extract()[0]

        item["size"] = qf.xpath('*/div[starts-with(text(),"Wohn")]/parent::div/text()').extract()[0]

        extras = qf.xpath('div[@class="merkmale"]/text()').extract()[0]
        item["extras"] = extras.split(',')

        yield item
