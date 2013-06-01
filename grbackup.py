#!/usr/bin/env python
# coding=utf-8
import sys
import time
import imp
import os
import logging
import getpass
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


def get_plugins(plugins_folder="grb_plugins"):
    """ Load plugins from folder
    and return dictionary {'plugin_type': 'module_instance'}
    args:
        plugins_folder - folder with plugins
    """
    plugins = {}
    # TODO: rewrite with package.subpackage path
    for plugin_module in os.listdir(plugins_folder):
        try:
            name = os.path.splitext(plugin_module)[0]
            _m = imp.find_module(name, [plugins_folder])
            m = imp.load_module(name, *_m)
            if hasattr(m, 'plugin_type'):
                plugins[m.plugin_type] = m
        except ImportError as err:
            logging.warn("Exception during loading module '%s': %r", name, err)
    return plugins


def get_active_plugin(output, plugins):
    for plugin_type in plugins:
        if plugin_type and options.output.split(":")[0] == plugin_type:
            return plugins[plugin_type]
            break
    else:
        logging.error("Can't find plugin for output '%s'" % options.output)
        exit(1)


def check_params(options):
    if (options.cmd_list and options.cmd_backup) or \
            not (options.cmd_list or options.cmd_backup):
        return "Please, specify --backup OR --list"

    if options.cmd_list and options.output:
        return "Option '--output' is ignored if '--list' specified"


def get_params(plugins):
    usage = "usage: grbackup [options] [args]"
    parser = OptionParser(usage=usage, conflict_handler="resolve")

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
                           action="store_true", help="processing all items")
    scope_group.add_option("-s", "--subscriptions", dest="scope_subs",
                           action="store_true", default=False,
                           help="processing subscriptions only")
    scope_group.add_option("-t", "--topics", dest="scope_topics",
                           default=False, action="store_true",
                           help="processing topics only")
    parser.add_option_group(scope_group)

    # Plugins Options
    for plugin in plugins:
        plugins[plugin].add_option_group(parser)

    # Other Options
    other_group = OptionGroup(parser, "Other Options")
    other_group.add_option("-o", "--output", dest="output",
                           default="json:backup.json", help="output path")
    other_group.add_option("-c", "--coding", dest="coding", default="utf8",
                           help="output coding [default: %default]")
    other_group.add_option("-v", "--verbose", action="store_true",
                           dest="verbose", default=False,
                           help="verbose output")
    parser.add_option_group(other_group)

    return parser.parse_args()


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


def main(options, args, plugins):
    if options.cmd_list:
        options.output = "simple://"
    plugin_output = get_active_plugin(options.output, plugins)

    while not options.email:
        options.email = raw_input("email: ")
    while not options.pwd:
        options.pwd = getpass.getpass("password: ")

    g = GReader(options.email, options.pwd)

    with plugin_output.writer(options) as plugin_writer:
        if options.scope_subs:
            for subscription in g.subscriptions:
                plugin_writer.put_subscription(subscription)

        elif options.scope_topics:
            subscription_url = args[0].encode(options.coding)
            if options.verbose:
                print("\n\n\nfeed: {url}\n".format(url=subscription_url))
            for post in g.posts(subscription_url):
                plugin_writer.put_topic(subscription_url, post)

        elif options.scope_all:
            for subscription in g.subscriptions:
                subscription_url = subscription['id'].encode(
                    options.coding)[5:]
                if options.cmd_list:
                    print("\n\n\nfeed: {url}\n".format(url=subscription_url))
                    plugin_writer.put_subscription(subscription)
                for post in g.posts(subscription_url):
                    plugin_writer.put_topic(subscription, post)


if __name__ == '__main__':
    plugins = get_plugins()
    options, args = get_params(plugins)
    check_result = check_params(options)
    if check_result:
        print(check_result)
        sys.exit(1)
    else:
        main(options, args, plugins)
