"""
Production settings, for use with Scrapinghub

Copyright 2018 Systema Development LLC
"""

from .base import *

import os
import json
from collections import ChainMap
import logging

log = logging.getLogger(f'{__package__}.{__name__}')

try:
    # get output bucket name from SHUB_SETTINGS
    blob = json.loads(os.environ['SHUB_SETTINGS'])
    env = ChainMap(*(blob.get(x, {}) for x in
                     ['job_settings'
                      'spider_settings',
                      'project_settings',
                      'organization_settings']))
    s3_bucket = env['S3_BUCKET']
except:
    log.error("Couldn't get S3_BUCKET, aborting", exc_info=True)
    raise SystemExit
else:
    log.info("Using S3 bucket %s for feeds", s3_bucket)

try:
    jobkey = os.environ['SHUB_JOBKEY']
except KeyError:
    log.info("Couldn't get SHUB_JOBKEY")
    jobkey = "unknown"

FEED_URI = f"s3://{s3_bucket}/feeds/{jobkey}/%(name)s-%(time)s.csv"
log.info("Storing feed at %s", FEED_URI)

CONCURRENT_REQUESTS = 2000
REACTOR_THREADPOOL_MAXSIZE = 20
AUTOTHROTTLE_START_DELAY = 0.5
AUTOTHROTTLE_MAX_DELAY = 5.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 8.0
ADBLOCK_DOWNLOAD = True
