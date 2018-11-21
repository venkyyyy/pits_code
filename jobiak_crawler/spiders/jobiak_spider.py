"""
Primary crawling logic

Copyright 2018 Systema Development LLC
"""

from scrapy.spiders import Spider
from scrapy import Request, FormRequest
from scrapy.http.request.form import _get_inputs as scrapy_get_inputs
from scrapy.utils.response import get_base_url
import tldextract
import formasaurus
from w3lib.html import strip_html5_whitespace
from urllib.parse import urljoin

from collections import defaultdict
from functools import partial
import importlib_resources

import re

from ..items import JobiakItem
from ..decorators import scrapy_stats, text_only
from ..state import State

def load_resource(name):
    """load a data file, skipping comments """
    fh = importlib_resources.open_text(f'{__package__}.data', name)
    return [l.rstrip() for l in fh if not l.startswith('#')]

def load_regex(name):
    """load a regex from data file"""
    return r'''(%s)''' % '|'.join(load_resource(name))

# breaks a URL into tokens
URL_DELIMITER = r'''[-_/.?&=]'''

# list of words to use in search forms to find a jobs index page
JOB_SEARCH_WORDS = load_resource("job_search_words.txt")

# a regex for URLs likely to contain jobs
JOB_URL_RE = re.compile(
    fr'''(^|(.*{URL_DELIMITER})){load_regex("job_url_words.txt")}(({URL_DELIMITER}.*)|$)''',
    re.IGNORECASE|re.UNICODE)

# a regex for anchor text likely to contain jobs
JOB_ANCHOR_RE = re.compile(fr'''\b{load_regex("job_anchor_words.txt")}\b''',
                         re.IGNORECASE|re.UNICODE)

# set of job board domains
JOB_BOARD_DOMAINS = frozenset(tldextract.extract(url).registered_domain
                              for url in load_resource('job_board_urls.txt'))

def is_job_board_url(url: str) -> bool:
    """check if the URL is from a known job board (matching domain name)"""
    return tldextract.extract(url).registered_domain in JOB_BOARD_DOMAINS

# a regex for deciding if a page is a job
IS_JOB_PAGE_RE = re.compile(fr'''\b{load_regex("is_job_keywords.txt")}\b''',
                            re.IGNORECASE|re.UNICODE)

def is_job_page(text: str) -> bool:
    """check if the text is a job"""
    return bool(IS_JOB_PAGE_RE.search(text))

class JobiakSpider(Spider):
    name = 'jobiak'

    # meta keys to persist across requests & respones
    sticky_meta = ('start_url', 'start_urls_file', 'state')

    # default start url if none passed from file
    start_urls = ['https://www.ibm.com/']

    @classmethod
    def from_crawler(self, *args, **kwargs):
        self = super().from_crawler(*args, **kwargs)
        self.max_requests_per_site = self.settings.getint('MAX_REQUESTS_PER_SITE')
        self.max_jobs_per_site = self.settings.getint('MAX_JOBS_PER_SITE')
        self.output_jobs_only = self.settings.getbool('OUTPUT_JOBS_ONLY')
        return self

    def start_requests(self):
        for r in super().start_requests():
            r.meta['start_url'] = r.url
            r.meta['link_type'] = 'start_url'

            # make a state - it deals with maintaing connection to this start_url itself
            State(r.url, self.crawler.stats, self.max_jobs_per_site, self.max_requests_per_site)
            r.dont_filter = True
            r.callback = self.parse_start
            yield r
            self.logger.info("Starting requests for %s", r.url)
            self.crawler.stats.inc_value('spider/start_requests', 1)

    def make_item(self, response):
        """make a JobiakItem"""
        item = JobiakItem()
        item['source_url'] = response.request.meta.get('source_url', '')
        item['start_url'] = response.meta['start_url']
        item['depth'] = response.request.meta['depth']
        item['link_type'] = response.request.meta['link_type']
        item['is_job'] = is_job_page(response.text)
        # everything else is done with magic or sticky fields
        return item

    def make_request(self, response, *args, form=None, formdata=None, link_type, **kwargs):
        """construct a new request

        Pass `form` (an lxml Element) and `formdata` (dict) to submit a `FormRequest`.
        """
        meta = {'source_url': response.url, 'link_type': link_type}
        if form is None:
            assert formdata is None
            return response.follow(meta=meta, *args, **kwargs)
        else:
            assert formdata is not None
            # from https://github.com/scrapy/scrapy/blob/master/scrapy/http/request/form.py#L39
            # which does not allow us to pass an already-found lxml form Element, unfortunately
            kwargs.setdefault('encoding', response.encoding)
            formdata = scrapy_get_inputs(form, formdata,
                                         dont_click=None, clickdata=None, response=response)

            base_url = get_base_url(response)
            action = form.get('action')
            url = base_url if action is None else urljoin(base_url, strip_html5_whitespace(action))
            method = kwargs.pop('method', form.method)
            return FormRequest(url=url, formdata=formdata, method=method,
                               meta=meta, *args, **kwargs)

    @scrapy_stats
    @text_only
    def parse(self, response):
        """default callback"""
        return self.parse_page(response)

    def parse_page(self, response):
        """implements logic called on all pages"""
        item = self.make_item(response)

        # maybe output the item
        if item["is_job"] or not self.output_jobs_only:
            yield item

        # output many Requests
        yield from (self.make_request(response, url, link_type=link_type)
                    for url, link_type in self.find_job_links(response))

    def find_job_links(self, response):
        """yield (url, link_type) for links likely to be job-related"""
        for node in response.css('a'):
            anchor = node.extract()
            url = node.attrib.get('href')
            full_url = response.urljoin(url)
            if JOB_ANCHOR_RE.search(anchor):
                self.crawler.stats.inc_value('spider/job_text_link')
                yield url, 'job_text_link'
            elif JOB_URL_RE.search(full_url):
                self.crawler.stats.inc_value('spider/job_url_link')
                yield url, 'job_url_link'
            elif  is_job_board_url(full_url):
                self.crawler.stats.inc_value('spider/job_board_link')
                yield url, 'job_board_link'

    @scrapy_stats
    @text_only
    def parse_start(self, response):
        i = 0  # count of links we found
        for i, x in enumerate(self.parse_page(response)):
            yield x

        # plug JOB_SEARCH_WORDS into site's search form(s)
        for form, info in formasaurus.extract_forms(response.text):
            if info['form'] == 'search':
                # find first search query field
                try:
                    field = next(k for k, v in info['fields'].items() if v == 'search query')
                except StopIteration:
                    # didn't find a field, go on to next form
                    continue

                for word in JOB_SEARCH_WORDS:
                    self.crawler.stats.inc_value('spider/site_search_link')
                    i += 1
                    yield self.make_request(response,
                                            link_type='site_search',
                                            form=form,
                                            formdata={field: word})

        if i == 0:
            self.logger.info("No links from start_url: %s", response.meta['start_url'])
            self.crawler.stats.inc_value('spider/no_links_from_start')
