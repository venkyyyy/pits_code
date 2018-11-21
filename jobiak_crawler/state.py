"""
Shared state

Copyright 2018 Systema Development LLC
"""

from scrapy.http import Request, Response
import threading

import logging
log = logging.getLogger(__name__)

class State:
    """Maintains shared per-`start_url` state, used for stopping conditions

    Used in various middlewares.
    """

    __instances__ = {}  # map of start_url => instance

    def __init__(self, start_url, stats, max_jobs, max_requests):
        self.start_url = start_url
        self.stats = stats
        self.max_jobs = max_jobs
        self.max_requests = max_requests
        self.jobs = 0
        self.requests = 0
        self.responses = 0
        self.late_responses = 0
        self._lock = threading.RLock()   # XXX scrapinghub seems to use threads. wat.
        self.__instances__[start_url] = self
        log.info("Created state for %s", start_url)

    @classmethod
    def get(cls, start_url):
        """get a state by `start_url`. You can also pass a Request or Response"""
        if isinstance(start_url, Request):
            start_url = start_url.meta['start_url']
        elif isinstance(start_url, Response):
            start_url = start_url.meta['start_url']
        else:
            raise TypeError(start_url)
        return cls.__instances__[start_url]

    def should_stop(self):
        """return True if stopping conditions are met"""
        with self._lock:
            return self.jobs >= self.max_jobs or self.requests >= self.max_requests

    def found_job(self, link_type, depth):
        """record finding a job"""
        with self._lock:
            # if this is the first job found for this site, record a stat
            if not self.jobs:
                self.stats.inc_value('found_job/sites', 1)

            # update state
            self.jobs += 1

            # record stats
            self.stats.inc_value('found_job', 1)
            self.stats.inc_value('found_job/%s' % link_type, 1)
            self.stats.inc_value('found_job/depth/%d' % depth, 1)
            self.bucket_stats('found_job/count', self.jobs)

            if self.jobs >= self.max_jobs:
                log.info("Found job, stopping for site %s with %d jobs and %d requests",
                         self.start_url, self.jobs, self.requests)

    def made_request(self):
        """record making request"""
        with self._lock:
            self.requests += 1
            self.bucket_stats('requests_per_site', self.requests)
            if self.requests >= self.max_requests:
                log.info("Request budget exceeded, stopping for site %s with %d jobs and %d requests",
                         self.start_url, self.jobs, self.requests)

    def got_response(self):
        """record receiving response"""
        with self._lock:
            self.responses += 1

            if self.should_stop():
                self.late_responses += 1
                log.info("Response after stop received for %s", self.start_url)
                self.stats.inc_value("response_after_stop", 1)
                self.bucket_stats("response_after_stop", self.late_responses)

    def bucket_stats(self, name, count):
        """record stats in buckets of 10, for internal use"""
        # increment bucket stats every 10th page
        bucket, rem = divmod(count, 10)
        bucket *= 10
        if bucket == 0 and rem == 1:
            # first request
            assert count == 1
            self.stats.inc_value(f'{name}/{bucket:0>3}-{bucket+9:0>3}', 1)
        elif rem == 0:
            # a bucket boundary
            assert bucket >= 10
            assert count >= 10
            self.stats.inc_value(f'{name}/{bucket:0>3}-{bucket+9:0>3}', 1)
            self.stats.inc_value(f'{name}/{bucket-10:0>3}-{bucket-1:0>3}', -1)
