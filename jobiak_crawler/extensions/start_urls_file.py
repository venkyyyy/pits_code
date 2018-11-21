"""
Extension to enable loading start_urls from a file on disk or S3

Copyright 2018 Systema Development LLC
"""

import logging
import urllib.request
import urllib.parse
import boto3
import contextlib
import codecs
import io

from scrapy import signals
from scrapy.exceptions import NotConfigured

log = logging.getLogger(__name__)

class StartUrlsFile:
    """Enables loading `start_urls` from a file or HTTP server"""

    @classmethod
    def from_crawler(cls, crawler):
        # first check if the extension should be enabled and raise
        # NotConfigured otherwise
        if not crawler.settings.getbool('START_URLS_FILE_ENABLED'):
            raise NotConfigured

        self = cls()
        self.settings = crawler.settings
        # connect the extension object to signals
        crawler.signals.connect(self.spider_opened, signal=signals.spider_opened)

        # return the extension object
        return self

    def spider_opened(self, spider):
        try:
            fname = getattr(spider, 'start_urls_file')
        except AttributeError:
            spider.start_urls_file = ''
        else:
            log.info("Reading start urls from %s for spider %s", fname, spider.name)

            # this may block, but that's ok, we're only called at spider startup
            if fname.startswith('s3'):
                fh = self.open_s3(fname)
            elif fname.startswith('http'):
                fh = codecs.EncodedFile(urllib.request.urlopen(fname), 'utf-8')
            else:
                fh = open(fname)

            with contextlib.closing(fh) as fh:
                spider.start_urls = [s if s.startswith('http') else f'http://{s}' for s in
                                     filter(None, (l.rstrip() for l in fh))]

            log.info("Read %d start urls", len(spider.start_urls))
            spider.crawler.stats.set_value('start_urls_file', len(spider.start_urls))

    def open_s3(self, uri):
        u = urllib.parse.urlparse(uri)
        bucketname = u.hostname
        access_key = u.username or self.settings['AWS_ACCESS_KEY_ID']
        secret_key = u.password or self.settings['AWS_SECRET_ACCESS_KEY']
        keyname = u.path[1:]  # remove first "/"
        s3 = boto3.client('s3',
                              aws_access_key_id=access_key,
                              aws_secret_access_key=secret_key)
        response = s3.get_object(Bucket=bucketname, Key=keyname)
        return io.StringIO(response['Body'].read().decode('utf-8'))
