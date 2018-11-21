"""
AdblockMiddleware, based on https://github.com/scrapinghub/adblockparser

Copyright 2018 Systema Development LLC
"""
from adblockparser import AdblockRules
import importlib_resources
import urllib
import codecs
import logging
from scrapy import Request

log = logging.getLogger(__name__)

class AdblockMiddleware:

    def __init__(self, download_rules, stats):
        """
        :arg bool download_rules: should we download rules or use bundled
        """
        self.stats = stats

        # all this supported_options nonsense is a major performance boost:
        # https://github.com/scrapinghub/adblockparser#parsing-rules-with-options
        self.supported_options = {k: True for k in
                                  ['script', 'popup', 'image', 'stylesheet', 'object']}


        self.rules = AdblockRules(self.load_rules(download_rules),
                                  supported_options=self.supported_options.keys(),
                                  skip_unsupported_rules=False)

    @staticmethod
    def load_rules(download_rules):
        if download_rules:
            log.info("Downloading latest EasyList rules")
            # lie about user agent since default is blocked
            req = urllib.request.Request("https://easylist.to/easylist/easylist.txt",
                                          headers={'User-Agent': 'Wget/1.17.1'})
            return codecs.iterdecode(urllib.request.urlopen(req), 'utf-8')
        else:
            log.info("Loading bundled EasyList rules, consider updating")
            return importlib_resources.open_text(f'{__package__}.data', 'easylist.txt')

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings.getbool('ADBLOCK_DOWNLOAD', False),
                   crawler.stats)

    def process_spider_output(self, response, result, spider):
        for x in result:
            if not isinstance(x, Request) or x.dont_filter:
                # not a request, just yield it
                yield x
            elif self.rules.should_block(x.url, options=self.supported_options):
                # adblock rules matched, silently drop it & increment stats
                self.stats.inc_value('adblock/filtered', spider=spider)
            else:
                # allow request
                yield x


