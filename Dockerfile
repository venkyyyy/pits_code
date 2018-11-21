# based on https://github.com/scrapinghub/scrapinghub-stack-scrapy/blob/branch-1.5-py3/Dockerfile

FROM python:3.6
ARG PIP_INDEX_URL
ARG PIP_TRUSTED_HOST
ARG APT_PROXY
ONBUILD ENV PIP_TRUSTED_HOST=$PIP_TRUSTED_HOST PIP_INDEX_URL=$PIP_INDEX_URL
ONBUILD RUN test -n $APT_PROXY && echo 'Acquire::http::Proxy \"$APT_PROXY\";' \
    >/etc/apt/apt.conf.d/proxy

# TERM needs to be set here for exec environments
# PIP_TIMEOUT so installation doesn't hang forever
ENV TERM=xterm \
    PIP_TIMEOUT=180 \
    SHUB_ENFORCE_PIP_CHECK=1

RUN apt-get update -qq && \
    apt-get install -qy \
        netbase ca-certificates apt-transport-https \
        build-essential locales \
        libxml2-dev \
        libssl-dev \
        libxslt1-dev \
        libevent-dev \
        libffi-dev \
        libpcre3-dev \
        libz-dev \
        telnet vim htop iputils-ping curl wget lsof git sudo \
        ghostscript
# http://unix.stackexchange.com/questions/195975/cannot-force-remove-directory-in-docker-build
#        && rm -rf /var/lib/apt/lists

## start our customizations

# additional dependencies
RUN apt-get install -qy \
    libre2-dev

# Add app directory to PYTHONPATH
ENV PYTHONPATH=$PYTHONPATH:/app

# tell scrapy which settings to use
ENV SCRAPY_SETTINGS_MODULE=jobiak_crawler.settings.prod

# get pipenv installed
RUN pip install --no-cache-dir pipenv

# make an app directory
RUN mkdir /app
COPY Pipfile Pipfile.lock /app/
WORKDIR /app

# install dependencies
ENV PIP_NO_CACHE_DIR=false
RUN set -x \
    && pipenv install --system --ignore-pipfile

# initialize formasaurus
RUN pipenv run formasaurus init

# Add our code
ADD . /app
