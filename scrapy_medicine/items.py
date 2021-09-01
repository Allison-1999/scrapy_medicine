# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyMedicineItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    #疾病名称
    disease_name=scrapy.Field()
    #药品名称
    medicine_name=scrapy.Field()
    #适应症
    indication=scrapy.Field()
    #主要成分
    components=scrapy.Field()
    #功能主治
    functions=scrapy.Field()
    #用量用法
    usage=scrapy.Field()
    pass
