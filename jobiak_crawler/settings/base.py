# -*- coding: utf-8 -*-
"""
Base settings for Jobiak crawler

Copyright 2018 Systema Development LLC
"""


# Scrapy settings for jobiak-crawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'jobiak-crawler'

SPIDER_MODULES = ['jobiak_crawler.spiders']
NEWSPIDER_MODULE = 'jobiak_crawler.spiders'

LOG_LEVEL = 'INFO'

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'jobiak_crawler.middlewares.MyCustomSpiderMiddleware': 543,
#}

SPIDER_MIDDLEWARES = {
    'scrapy_querycleaner.QueryCleanerMiddleware': 100,
    'scrapy_magicfields.MagicFieldsMiddleware': 501,
    'stickymeta.StickyMetaMiddleware': 502,
    'jobiak_crawler.spidermiddlewares.protocol.ProtocolMiddleware': 503,
    'jobiak_crawler.spidermiddlewares.filename.FilenameMiddleware': 504,
    # XXX disabled, because it's very rarely used
    # 'jobiak_crawler.spidermiddlewares.adblock.AdblockMiddleware': 505,
    'jobiak_crawler.spidermiddlewares.pagination.PagintationMiddleware': 506,
    'jobiak_crawler.spidermiddlewares.state.StateSpiderMiddleware': 1000,
}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # just after robots.txt and before any middlewares that re-issue requests
    'jobiak_crawler.downloadermiddlewares.state.StateDownloaderMiddleware': 101,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}
EXTENSIONS = {
    'jobiak_crawler.extensions.start_urls_file.StartUrlsFile': 100,
    'scrapy_fieldstats.fieldstats.FieldStatsExtension': 901,
}
START_URLS_FILE_ENABLED = True
FIELDSTATS_ENABLED = True

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'jobiak-crawler (+http://www.jobiak.ai)'
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Force a specific SSL version
DOWNLOADER_CLIENT_TLS_METHOD = 'TLSv1.2'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs

# Minimum delay for autothrottle
DOWNLOAD_DELAY = 0.1

# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 3.0
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 30
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Global limits
DEPTH_STATS_VERBOSE = True
DEPTH_LIMIT = 5
DOWNLOAD_MAXSIZE = 2 * 1024 * 1024  # 2 MB
MAX_REQUESTS_PER_SITE = 200
MAX_JOBS_PER_SITE = 1

# URL cleaning & adblock
QUERYCLEANER_REMOVE = 'sessionid|jsessionid|affiliateid|utm_source|utm_medium|utm_campaign|utm_term|utm_content'

# Automatically populated fields on Items
MAGIC_FIELDS = {
    'timestamp': '$isotime',
    'scrapy_job_id': '$jobid',
    'start_urls_file': '$spider:start_urls_file',
    'url': '$response:url',
}

# Output
FEED_FORMAT = 'csv'
FEED_EXPORT_FIELDS = ['start_url', 'url', 'is_job', 'link_type', 'source_url', 'depth',
                      'timestamp', 'scrapy_job_id']

# should we only output jobs, or all urls?
OUTPUT_JOBS_ONLY = True
