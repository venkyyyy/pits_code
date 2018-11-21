"""
Helpful decorators for spiders

Copyright 2018 Systema Development LLC
"""

from functools import wraps

def scrapy_stats(func):
    """decorator that records a stat 'spider/<wrapped function name>'"""
    @wraps(func)
    def wrapped(self, response, *args, **kwargs):
        self.crawler.stats.inc_value(f'spider/{func.__name__}')
        return func(self, response, *args, **kwargs)
    return wrapped

def text_only(func):
    """drops non-text responses that somehow wound up back at spider"""
    @wraps(func)
    def wrapped(self, response, *args, **kwargs):
        if not hasattr(response, 'text'):
            self.crawler.stats.inc_value('spider/non_text_response')
            return None
        else:
            return func(self, response, *args, **kwargs)
    return wrapped
