#!/usr/bin/env python
# coding=utf-8
from optparse import OptionGroup
import pymongo


plugin_type = "mongodb"


def add_option_group(parser):
    # MongoDB Options
    mongodb_group = OptionGroup(parser, "MongoDB Options")
    mongodb_group.add_option("--mongodb-database",
                             dest="mongodb_database",
                             type="str",
                             default="greader",
                             help="the name of the database"
                             "[default: %default]")
    mongodb_group.add_option("--mongodb-subscriptions",
                             dest="mongodb_subscriptions",
                             default='subscriptions',
                             type="str",
                             help="collection name for subscriptions"
                             "[default: %default]")
    mongodb_group.add_option("--mongodb-topics",
                             dest="mongodb_topics",
                             default='topics',
                             type="str",
                             help="collection name for topics"
                             "[default: %default]")
    mongodb_group.add_option("--mongodb-w",
                             dest="mongodb_w",
                             default=1,
                             type=int,
                             help="<int> Write operations will block until "
                             "they have been replicated to the "
                             "specified number [default: %default]")
    mongodb_group.add_option("--mongodb-j",
                             dest="mongodb_j",
                             default=False,
                             action="store_true",
                             help="block until write operations "
                             "have been committed to the journal "
                             "[default: %default]")
    parser.add_option_group(mongodb_group)


class WriteMongoDB(object):

    def __init__(self, uri, collection_subsr, collection_topics,
                 w, j, db=None):
        self.uri = uri
        self._subscriptions = collection_subsr
        self._topics = collection_topics
        uri_info = pymongo.uri_parser.parse_uri(uri)
        self.db = db or uri_info['database']
        Client = pymongo.MongoClient
        if uri_info['options'].get('replicaset'):
            Client = pymongo.MongoReplicaSetClient
        self.conn = Client(uri, w=w, j=j)
        self.sids = []  # subscriptions ids to avoid dublication

    def put_subscription(self, subscription):
        if subscription['id'] not in self.sids:
            self.conn[self.db][self._subscriptions].insert(subscription)
            self.sids.append(subscription['id'])

    def put_topic(self, subscription, topic):
        if not isinstance(subscription, str):
            self.put_subscription(subscription)
        self.conn[self.db][self._topics].insert(topic)


class writer(object):

    def __init__(self, opt):
        self._output = opt.output
        self.subsr = opt.mongodb_subscriptions
        self.topics = opt.mongodb_topics
        self.db = opt.mongodb_database
        self.w = opt.mongodb_w
        self.j = opt.mongodb_j

    def __enter__(self):
        return WriteMongoDB(self._output,
                            self.subsr, self.topics,
                            self.w, self.j, db=self.db)

    def __exit__(self, *exc_info):
        pass
