#!/usr/bin/env python
# coding=utf-8
import sys
import time
import logging
from optparse import OptionParser, OptionGroup
from greader import GReader


root_logger = logging.getLogger()
root_logger.setLevel(logging.ERROR)


def loading(text, callback_exit, callback_count=None):
    print(text),
    sys.stdout.flush()
    i = 0
    _load = ('\b/', '\b-', '\b\\', '\b|')

    while not callback_exit():
        sys.stdout.write(_load[i % 4])
        sys.stdout.flush()
        time.sleep(0.2)
        if i > 4:
            i = 0
        else:
            i += 1

    print '\b\b Done!'


def get_params():
    usage = "usage: grbackup [options] [args]"
    parser = OptionParser(usage=usage)

    # Auth Options
    auth_group = OptionGroup(parser, "Auth Options")
    auth_group.add_option("-e", "--email", dest="email",
                          help="gmail account")
    auth_group.add_option("-p", "--password", dest="pwd",
                          help="account password")
    parser.add_option_group(auth_group)

    # Command Options
    cmd_group = OptionGroup(parser, "Command Options")
    cmd_group.add_option("-b", "--backup", dest="cmd_backup", default=False,
                         action="store_true", help="backup items")
    cmd_group.add_option("-l", "--list", dest="cmd_list", default=False,
                         action="store_true", help="list items")
    parser.add_option_group(cmd_group)

    # Scope Options
    scope_group = OptionGroup(parser, "Scope Options")
    scope_group.add_option("-a", "--all", dest="scope_all", default=False,
                           action="store_true", help="list/backup all items")
    scope_group.add_option("-s", "--subscriptions", dest="scope_subs",
                           action="store_true", default=False,
                           help="list/backup subscriptions only")
    scope_group.add_option("-t", "--topics", dest="scope_topics",
                           default=False, action="store_true",
                           help="list/backup topics only")
    parser.add_option_group(scope_group)

    # Other Options
    other_group = OptionGroup(parser, "Other Options")
    other_group.add_option("-o", "--output", dest="output", help="output file")
    other_group.add_option("-c", "--coding", dest="coding", default="utf8",
                           help="output coding [default: %default]")
    other_group.add_option("-v", "--verbose", action="store_true",
                           dest="verbose", default=False,
                           help="verbose output")
    parser.add_option_group(other_group)

    return parser.parse_args()


def print_subscription(subscription, coding, head=""):
    title = subscription['title'].encode(coding)
    url = subscription['id'].encode(coding)[5:]
    print("{0}{1} ({2})".format(head, title, url))


def print_topics(topic, coding, head=""):
    date = {'updated': topic['updated'],
            'published': topic['published']}
    url = topic['alternate'][0]['href'].encode(coding)
    title = topic['title'].encode(coding)
    message = '{head}{title} ({url})'.format(
        head=head, date=date, title=title, url=url)
    print(message)


if __name__ == '__main__':
    options, args = get_params()
    while not options.email:
        options.email = raw_input("email: ")
    while not options.pwd:
        options.pwd = raw_input("password: ")

    g = GReader(options.email, options.pwd)
    # TODO: check_options()

    if options.scope_subs:
        for index, subscription in enumerate(g.subscriptions, 1):
            if options.cmd_list:
                print_subscription(subscription,
                                   options.coding,
                                   "{0} ".format(index))

    elif options.scope_topics:
        subscription_url = args[0].encode(options.coding)
        if options.verbose:
            print("\n\n\nfeed: {url}\n".format(url=subscription_url))
        if options.cmd_list:
            for index, post in enumerate(g.posts(subscription_url), 1):
                print_topics(post, options.coding, "{0} ".format(index))

    elif options.scope_all:
        for subscription in g.subscriptions:
            subscription_url = subscription['id'].encode(options.coding)[5:]
            print("\n\n\nfeed: {url}\n".format(url=subscription_url))
            for index, post in enumerate(g.posts(subscription_url), 1):
                print_topics(post, options.coding, "{0} ".format(index))
