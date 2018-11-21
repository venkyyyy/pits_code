"""
Filter requests by protocol

Copyright 2018 Systema Development LLC
"""
from scrapy import Request
import urllib.parse

class ProtocolMiddleware:

    def __init__(self, allowed_protocols, stats):
        self.stats = stats
        self.allowed_protocols = frozenset(allowed_protocols)

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings.getlist('ALLOWED_PROTOCOLS', ('http', 'https')),
                   crawler.stats)

    def process_spider_output(self, response, result, spider):
        for x in result:
            if not isinstance(x, Request) or x.dont_filter:
                # not a request, just yield it
                yield x
            elif urllib.parse.urlparse(x.url).scheme not in self.allowed_protocols:
                # bad protocol, silently drop it & increment stats
                self.stats.inc_value('protocol/filtered', spider=spider)
            else:
                # allow request
                yield x


