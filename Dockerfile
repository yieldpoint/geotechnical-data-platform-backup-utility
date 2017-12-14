FROM jfloff/alpine-python:2.7
MAINTAINER YieldPoint <admin@yieldpoint.com>

RUN apk update && apk upgrade &&  \
    apk add mysql mysql-client && \
    addgroup mysql mysql && \
    mkdir /scripts && \
    rm -rf /var/cache/apk/*

