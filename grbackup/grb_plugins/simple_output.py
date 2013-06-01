#!/usr/bin/env python
# coding=utf-8
from collections import defaultdict


plugin_type = "simple"


def add_option_group(parser):
    return None


def print_subscription(subscription, coding, head=""):
    title = subscription.get('title', '').encode(coding)
    url = subscription['id'].encode(coding)[5:]
    print("{0}{1} ({2})".format(head, title, url))


def print_topics(topic, coding, head=""):
    date = {'updated': topic['updated'],
            'published': topic['published']}
    url = ''
    if topic.get('alternate'):
        url = topic['alternate'][0]['href'].encode(coding)
    title = topic.get('title', '').encode(coding)
    message = '{head}{title} ({url})'.format(
        head=head, date=date, title=title, url=url)
    print(message)


class SimplePrint(object):

    def __init__(self, coding):
        self.coding = coding
        self._count_subs = 0
        self._count_topics = defaultdict(int)
        self._subscription = None

    def put_subscription(self, subscription):
        self._count_subs += 1
        title = subscription.get('title', '').encode(self.coding)
        url = subscription['id'].encode(self.coding)[5:]
        print("{0}: {1} ({2})".format(self._count_subs, title, url))

    def put_topic(self, subscription, topic):
        if subscription != self._subscription:
            self._subscription = subscription
            self._count_topics = 0
        self._count_topics += 1
        url = ''
        if topic.get('alternate'):
            url = topic['alternate'][0]['href'].encode(self.coding)
        title = topic.get('title', '').encode(self.coding)
        message = '{0}: {1} ({2})'.format(self._count_topics, title, url)
        print(message)


class writer(object):

    def __init__(self, opt):
        self._coding = opt.coding

    def __enter__(self):
        return SimplePrint(self._coding)

    def __exit__(self, *exc_info):
        pass
