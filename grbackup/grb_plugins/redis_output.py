#!/usr/bin/env python
# coding=utf-8
import redis


plugin_type = "redis"


class WriteRedis(object):

    def __init__(self, uri):
        self.uri = uri
        self.conn = redis.StrictRedis.from_url(self.uri)

    def put_subscription(self, subscription):
        key = "subscription:{0}".format(subscription['id'])
        if not self.conn.exists(key):
            self.conn.hmset(key, subscription)

    def put_topic(self, subscription, topic):
        key = "topic:{0}".format(topic['id'])
        if not isinstance(subscription, str):
            self.put_subscription(subscription)
        if not self.conn.exists(key):
            self.conn.hmset(key, topic)


class writer(object):

    def __init__(self, opt):
        self._output = opt.output

    def __enter__(self):
        return WriteRedis(self._output)

    def __exit__(self, *exc_info):
        pass
