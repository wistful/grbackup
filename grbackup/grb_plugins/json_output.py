#!/usr/bin/env python
# coding=utf-8
import json
import os


plugin_type = "json"


def add_option_group(parser):
    return None


class WriteJSON(object):

    def __init__(self, fd):
        self.fd = fd

    def put_subscription(self, subscription):
        self.write({"type": "subscription", "value": subscription})

    def put_topic(self, subscription, topic):
        self.write({"type": "topic",
                    "subscription": subscription,
                    "value": topic})

    def write(self, json_obj):
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
