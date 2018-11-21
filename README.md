# Jobiak Crawler

Based [Scrapy](http://scrapy.org), the crawler takes an input list of seed URLs
and outputs a CSV file. Hosted deployment & dashboard on [Scrapinghub](http://scrapinghub.com),
inputs and outputs stored on S3.

Copyright 2018 Systema Development LLC

## Installation
You will need [https://docs.docker.com/install/](Docker) and Python 3.6 or later.
[https://docs.pipenv.org/install/](Install pipenv):
```
$ pip install --user pipenv
```

Change to the source directory and install dependencies
```
$ cd jobiak-crawler
$ pipenv install --dev
```

## Set up accounts

Do this only once.

### AWS
1. Create an AWS S3 Bucket and IAM user with read/write/list permissions to it.
2. Save the user's keys to a `.env` file in the source directory:

```
AWS_ACCESS_KEY_ID=<key id>
AWS_SECRET_ACCESS_KEY=<key secret>
```

### Scrapinghub

1. Create an account on [Scrapinghub](https://scrapinghub.com/)
2. Sign in to the [dashboard](https://app.scrapinghub.com/)
3. Buy Scrapy Cloud units. Click *Billing* in the left bar,
   then under *Scrapy Cloud*, click *Modify*. Buy units in multiples of 6 and click *Subscribe*
3. Create a project. In the top bar, click *Scrapy Cloud* then *Create Project*.
   Give you project a name, and choose *Scrapy*, then click *Create*.
4. Log in to your account. In a terminal, change to the project directory and run:
```
$ pipenv run shub login
```
5. Copy `scrapinghub.yml.template` in the source directory to `scrapinghub.yml`
   and set the `project` to the ID of your new Scrapinghub project.

```
project: <project id>
requirements:
  file: Pipfile.lock
image: true
version: GIT
```
6. Add AWS keys to Scrapinghub. In left bar, click *Settings*, then the *Raw Settings* tab.
   Enter the following values, and click *Save*:

```
AWS_ACCESS_KEY_ID=<key id>
AWS_SECRET_ACCESS_KEY=<key secret>
S3_BUCKET=<s3 bucket>
```

## Deployment

Deployment is managed with [Shub](https://shub.readthedocs.io/).

```
$ pipenv run shub deploy
```

Upload starting urls to S3:

```
pipenv run aws s3 cp urls-00.txt s3://<s3 bucket>/start-urls/urls-00.txt
```

## Running Jobs
Schedule a crawl. Pass the name of the inputfile with `-a start_urls_file=<path on s3>`.
Set a maximum runtime in seconds if you want with `-s CLOSESPIDER_TIMEOUT=43200` (12 hours).

```
$ pipenv run shub schedule jobiak \
  -u 6 \
  -a start_urls_file=s3://<s3 bucket>/start-urls/urls-00.txt \
  -s CLOSESPIDER_TIMEOUT=43200
```

You can monitor the crawl in the dashboard.

### Download Feed results
Download the results. The filename will be in the logs in the dashboard. To download all files:

```
pipenv run aws s3 sync s3://<s3 bucket>/feeds/<project id>/<spider id>/ feeds/
```

## Configuration

### Settings

Settings can overriden in the *Settings* for the Scrapinghub project. Interesting settings include:
* `OUTPUT_JOBS_ONLY`: should we write CSV rows for only jobs or all pages? Defaults to true.
* `MAX_REQUESTS_PER_SITE`: maximum number of requests to make for a given start_url. Defaults to 200.
* `MAX_JOBS_PER_SITE`: stop crawling a particular site after finding this many jobs.
  This number is approximate, and more jobs may be returned in some cases.

### Keyword lists
Keyword lists are in the `jobiak_crawler/spiders/data/` directory.
They are built in to the image; you will need to re-deploy if you modify them.

* `is_job_keywords.txt`: used to decide if a page is a job
* `job_anchor_words.txt`: words in anchor text of links to follow
* `job_board_urls.txt`: URLs of known job boards
* `job_search_words.txt`: words to plug in to a site's search form
* `job_url_words.txt`: words in URLs of links to follow

## Input format
A text file of starting urls with one URL per file. For best results, please use at least 5,000 urls
in a file (approximately 1 hour running time). Fewer URLs per file will _not_ go faster. You can run
multiple crawls in parallel by buying more units, and splitting up the input into multiple files.

## Output format
A CSV file with the following fields:

* `start_url`: the starting url
* `url`: the url of the page
* `is_job`: boolean, is this page a job?
* `link_type`: how the current page was found
* `source_url`: url of page that linked to this one
* `depth`: number of links from start_url
* `timestamp`: time page was crawled
* `scrapy_job_id`: Scrapinghub job identifier

Only job URLs are included. To include all pages visited, set `OUTPUT_JOBS_ONLY` setting to False.
