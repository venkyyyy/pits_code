"""
Filter requests by filename extension

Copyright 2018 Systema Development LLC
"""
from scrapy import Request
from scrapy.utils.url import url_has_any_extension
from scrapy.linkextractors import IGNORED_EXTENSIONS

import logging
log = logging.getLogger(__name__)

class FilenameMiddleware:

    def __init__(self, ignored_extensions, stats):
        self.stats = stats
        log.info("Ignoring extensions %r", ignored_extensions)
        self.ignored_extenstions = frozenset(f".{e}" for e in ignored_extensions)

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings.getlist('IGNORED_EXTENSIONS', IGNORED_EXTENSIONS),
                   crawler.stats)

    def process_spider_output(self, response, result, spider):
        for x in result:
            if not isinstance(x, Request) or x.dont_filter:
                # not a request, just yield it
                yield x
            elif url_has_any_extension(x.url, self.ignored_extenstions):
                # extension matched, silently drop it & increment stats
                self.stats.inc_value('filename/filtered', spider=spider)
                log.debug("Ignoring request <%s>: extension not allowed", x.url)
            else:
                # allow request
                self.stats.inc_value('filename/allowed', spider=spider)
                yield x


