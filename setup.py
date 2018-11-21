# Automatically created by: shub deploy

from setuptools import setup, find_packages

setup(
    name='jobiak-crawler',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'scrapy': [
            'settings = jobiak_crawler.settings',
        ],
    },
    # These scripts will be available as "Periodic Jobs".
    scripts=[
        'bin/archive-items.py',
    ],
)
