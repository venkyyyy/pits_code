"""
Maintain State

Copyright 2018 Systema Development LLC
"""
from scrapy import Request
from scrapy.exceptions import IgnoreRequest

from ..state import State

import logging
log = logging.getLogger(__name__)

class StateDownloaderMiddleware:

    def __init__(self, stats):
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats)

    def process_request(self, request, spider):
        state = State.get(request)
        if state.should_stop():
            raise IgnoreRequest
        else:
            state.made_request()
            return None  # continue middlware chain

    def process_response(self, request, response, spider):
        state = State.get(request)
        state.got_response()
        return response
