"""
Development settings

Copyright 2018 Systema Development LLC
"""

from .base import *
from pathlib import Path

CLOSESPIDER_PAGECOUNT = 300
MAX_REQUESTS_PER_SITE = 100

# save feed to ~/jobiak.csv
FEED_URI = (Path.home() / 'jobiak.csv').as_uri()
OUTPUT_JOBS_ONLY = False

# disable adblock in dev, b/c startup takes forerver
SPIDER_MIDDLEWARES['jobiak_crawler.spidermiddleware.adblockmiddleware.AdblockMiddleware'] = None

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


