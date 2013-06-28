#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""The MIT License (MIT)

Copyright (c) 2013 wistful

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE."""

__version__ = '1.2'
__author__ = 'wistful'
__url__ = 'https://github.com/wistful/SGR'
__license__ = 'The MIT License'
__copyright__ = '2013, wistful <wst.public.mail@gmail.com>'

import logging
import urllib2

from urllib import urlencode as url_encode
from urllib import quote as url_quote
from urllib import unquote as url_unquote

import re
import json

AUTH_URL = 'https://www.google.com/accounts/ClientLogin'
SUBSCRIPTIONS_LIST_URL = 'http://www.google.com/reader/api/0/subscription/list'
SUBSCRIPTION_URL = 'http://www.google.com/reader/api/0/stream/contents/feed/'
STARRED_URL = r"http://www.google.com/reader/api/0/stream/contents/user/-/" \
    "state/com.google/starred"


class GReader(object):

    def __init__(self, email=None, pwd=None):
        """
        Initializes GReader instance
        and authorizate if 'email' and 'pwd' setted
        Args:
            email - email address
            pwd - password
        """
        self._header = {}
        self._subscriptions = []
        self.__auth = bool(email and pwd and self.auth(email, pwd))

    def auth(self, email, pwd):
        """
        authorization to Google Reader service
        Args:
            email - email address
            pwd - password
        """
        req_data = url_encode(
            {'Email': email,
             'Passwd': pwd,
             'service': 'reader',
             'accountType': 'GOOGLE'})
        req = urllib2.Request(AUTH_URL, data=req_data)
        try:
            resp = urllib2.urlopen(req).read()
            token = re.search('Auth=(\S*)', resp).group(1)
            self._header = {
                'Authorization': 'GoogleLogin auth={token}'.format(
                    token=token)}
        except (urllib2.HTTPError, urllib2.URLError) as exc:
            logging.error("Login Failed: %s", exc)
        except AttributeError:
            logging.error("Token Not Found in the response.",
                          extra={'response': resp})
        self.__auth = True

    @property
    def is_auth(self):
        """
        return True if authorizate, else False
        """
        return self.__auth

    @property
    def subscriptions(self):
        """
        return list of subscriptions
        """
        if not self._subscriptions:
            req_data = url_encode({'output': 'json'})
            url = "{subscriptions_list_url}?{req_data}".format(
                subscriptions_list_url=SUBSCRIPTIONS_LIST_URL,
                req_data=req_data)
            req = urllib2.Request(url, headers=self._header)
            try:
                resp = urllib2.urlopen(req).read()
                self._subscriptions = json.loads(resp)['subscriptions']
            except (urllib2.HTTPError, urllib2.URLError) as exc:
                logging.error("Failed getting subscriptions: %s", exc)
            except KeyError:
                logging.error("Subscriptions not found in the response.",
                              extra={'response': resp})
        return self._subscriptions

    def get_items(self, url, count=20):
        """
        return return items from stream by url
        """
        logging.info('start fetching url %s ', url_unquote(url))
        req_param = {'r': 'n', 'n': count, 'client': 'scroll'}
        continuation = None
        while True:
            if continuation:
                req_param['c'] = continuation
            req_data = url_encode(req_param)
            feed_url = "{url}?{req_data}".format(url=url, req_data=req_data)
            req = urllib2.Request(feed_url, headers=self._header)
            try:
                resp = urllib2.urlopen(req).read()
            except (urllib2.HTTPError, urllib2.URLError) as exc:
                logging.error("Failed getting stream (%s) items: %s", url_unquote(url), exc)
                break
            feed_posts = json.loads(resp)

            for post in feed_posts['items']:
                yield post

            continuation = feed_posts.get('continuation', None)
            if not continuation:
                logging.info('end fetching url %s ', url_unquote(url))
                break

    def posts(self, subscription_url, count=20):
        """
        return posts of subscriptions
        """
        url = "{subscription_url}{subscription}".format(
            subscription_url=SUBSCRIPTION_URL,
            subscription=url_quote(subscription_url, '')
        )
        return self.get_items(url, count)

    def starred(self, count=20):
        """
        return starred posts
        """
        return self.get_items(STARRED_URL)
