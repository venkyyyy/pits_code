"""
Maintain State

Copyright 2018 Systema Development LLC
"""
from scrapy import Request

from ..state import State
from ..items import JobiakItem

import logging
log = logging.getLogger(__name__)

class StateSpiderMiddleware:

    def __init__(self, stats):
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats)

    def process_spider_output(self, response, result, spider):
        state = State.get(response)
        for x in result:
            if isinstance(x, JobiakItem):
                if x['is_job']:
                    state.found_job(response.meta['link_type'], response.meta['depth'])

                # always yield item
                yield x
            elif isinstance(x, Request):
                # filter requests early to reduce useless load in downloader
                # we increment state.pages only in downloadermiddleware
                if not state.should_stop() or x.dont_filter:
                    yield x



