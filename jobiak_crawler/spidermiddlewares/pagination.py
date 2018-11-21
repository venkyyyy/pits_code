"""
Filter out pagination urls

Copyright 2018 Systema Development LLC
"""
from scrapy import Request
import autopager

import logging
log = logging.getLogger(__name__)

class PagintationMiddleware:

    def __init__(self, stats):
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(crawler.stats)

    def process_spider_output(self, response, result, spider):
        if not hasattr(response, 'text'):
            # non text response, just return
            return result

        pagination_urls = set(autopager.urls(response))
        for x in result:
            if not isinstance(x, Request) or x.dont_filter:
                yield x
            elif x.url in pagination_urls:
                # drop pagination links
                self.stats.inc_value('pagination_url/filtered', 1)
            else:
                yield x
