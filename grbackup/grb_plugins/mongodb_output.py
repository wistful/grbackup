#!/usr/bin/env python
# coding=utf-8
from optparse import OptionGroup
import pymongo


plugin_type = "mongodb"


def add_option_group(parser):
    # MongoDB Options
    mongodb_group = OptionGroup(parser, "MongoDB Options")
    mongodb_group.add_option("--mongodb-db",
                             dest="mongodb_db",
                             type="str",
                             default="greader",
                             help="the name of the database"
                             "[default: %default]")
    mongodb_group.add_option("--mongodb-scol",
                             dest="mongodb_subscriptions",
                             default='subscriptions',
                             type="str",
                             help="collection name for subscriptions"
                             "[default: %default]")
    mongodb_group.add_option("--mongodb-tcol",
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
        uri_info = pymongo.uri_parser.parse_uri(uri)
        self.db = db or uri_info['database']
        Client = pymongo.MongoClient
        if uri_info['options'].get('replicaset'):
            Client = pymongo.MongoReplicaSetClient
        self.conn = Client(uri, w=w, j=j)
        self.scol = self.conn[self.db][collection_subsr]
        self.tcol = self.conn[self.db][collection_topics]

    def put_subscription(self, subscription):
        if not self.scol.find_one({'id': subscription['id']}):
            self.scol.insert(subscription)

    def put_topic(self, subscription, topic):
        if not isinstance(subscription, str):
            self.put_subscription(subscription)
        if not self.tcol.find_one({'id': topic['id']}):
            self.tcol.insert(topic)


class writer(object):

    def __init__(self, opt):
        self._output = opt.output
        self.subsr = opt.mongodb_subscriptions
        self.topics = opt.mongodb_topics
        self.db = opt.mongodb_db
        self.w = opt.mongodb_w
        self.j = opt.mongodb_j

    def __enter__(self):
        return WriteMongoDB(self._output,
                            self.subsr, self.topics,
                            self.w, self.j, db=self.db)

    def __exit__(self, *exc_info):
        pass
