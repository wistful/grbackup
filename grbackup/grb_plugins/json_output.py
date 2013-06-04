#!/usr/bin/env python
# coding=utf-8
import json
import os
import threading


plugin_type = "json"
support_threads = True
description = """save items into file
output scheme:   json:/path/to/file.json
output examples: json:/home/grbackup/grbackup.json
                 json:/tmp/grbackup/grbackup.json
"""


def add_option_group(parser):
    return None


class WriteJSON(object):

    def __init__(self, fd):
        self.fd = fd
        self.subscriptions = set()
        self.lock = threading.Lock()

    def put_subscription(self, subscription):
        if subscription['id'] not in self.subscriptions:
            self.subscriptions.add(subscription['id'])
            self.write({"type": "subscription", "value": subscription})

    def put_all(self, subscription, topic):
        self.put_subscription(subscription)
        subscription_url = subscription['id'][5:]
        self.put_topic(subscription_url, topic)

    def put_starred(self, topic):
        self.write({"type": "starred",
                    "value": topic})

    def put_topic(self, subscription_url, topic):
        self.write({"type": "topic",
                    "subscription": subscription_url,
                    "value": topic})

    def write(self, json_obj):
        with self.lock:
            if self.fd.tell() == 0:
                self.fd.write("[")
            else:
                self.fd.seek(-1, os.SEEK_END)
                self.fd.truncate()
                self.fd.write(",\n")
            self.fd.write(json.dumps(json_obj))
            self.fd.write("]")


class writer(object):

    def __init__(self, opt):
        self._output = opt.output[opt.output.index(":") + 1:]
        self._fd = open(self._output, 'w')

    def __enter__(self):
        return WriteJSON(self._fd)

    def __exit__(self, *exc_info):
        if self._fd:
            self._fd.close()
