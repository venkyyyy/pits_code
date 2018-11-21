# -*- coding: utf-8 -*-
"""
Data to collect

Copyright 2018 Systema Development LLC
"""
# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class JobiakItem(scrapy.Item):
    start_url = scrapy.Field()
    source_url = scrapy.Field()
    depth = scrapy.Field()
    timestamp = scrapy.Field()
    scrapy_job_id = scrapy.Field()
    start_urls_file = scrapy.Field()
    url = scrapy.Field()
    link_type = scrapy.Field()
    is_job = scrapy.Field()
