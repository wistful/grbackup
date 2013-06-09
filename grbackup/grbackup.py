#!/usr/bin/env python
# coding=utf-8
import sys
import imp
import os
import logging
import getpass
from optparse import OptionParser, OptionGroup

from threading import Thread
from Queue import Queue

from .greader import GReader


root_logger = logging.getLogger()
root_logger.setLevel(logging.WARNING)


def get_plugins():
    """ Load plugins from folder
    and return dictionary {'plugin_type': 'module_instance'}
    """
    plugins_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "grb_plugins")
    plugins = {}

    for plugin_module in os.listdir(plugins_folder):
        try:
            name = os.path.splitext(plugin_module)[0]
            _m = imp.find_module(name, [plugins_folder])
            m = imp.load_module(name, *_m)
            if hasattr(m, 'plugin_type'):
                plugins[m.plugin_type] = m
        except ImportError as err:
            message = "Exception during loading module '%s': %r" % (name, err)
            logging.warn(message)
    return plugins


def get_active_plugin(output, plugins):
    for plugin_type in plugins:
        if plugin_type and output.split(":")[0] == plugin_type:
            return plugins[plugin_type]
            break
    else:
        logging.error("Can't find plugin for output '%s'" % output)
        exit(1)


def check_params(options):
    if (options.cmd_list and options.cmd_backup) or \
            not (options.cmd_list or options.cmd_backup):
        return "Please, specify --backup OR --list"

    if options.cmd_list and not options.output.startswith("simple:"):
        print("Option '--output' is ignored if '--list' specified")


def make_usage(plugins):
    usage = "usage: grbackup [options] [args]"
    usage += """

Examples:

   list subscriptions: grbackup -e email@gmail.com -p password -ls
   list topics: grbackup -e email@gmail.com -p password -lt http://feed.com
   list starred: grbackup -e email@gmail.com -p password -lx
   list all items: grbackup -e email@gmail.com -p password -la

   backup subscriptions: grbackup -e email@gmail.com -p password -bs -o json:/tmp/subscriptions.json
   backup topics: grbackup -e email@gmail.com -p password -bt http://myfeed.com -o json:/tmp/myfeed.json
   backup starred into MongoDB: grbackup -e email@gmail.com -p password -bx -o mongodb://localhost:27017
   backup all items into Redis: grbackup -e email@gmail.com -p password -ba -o redis://localhost:6379/3

"""
    usage += "Available plugins:\n\n"

    maxlen = max([len(plugin_name) for plugin_name in plugins]) + 2
    lines = []
    for name, m in plugins.items():
        if name == "simple":
            continue
        formatted_str = '  {0:{alignment}{length}} {1}'
        descr = getattr(m, 'description', '').split('\n')
        for i, col2 in enumerate(descr):
            col1 = name + ":" if i == 0 else ""
            lines.append(formatted_str.format(col1, col2,
                                              alignment='<',
                                              length=maxlen))

    usage += "\n".join(lines)
    return usage


def get_params(plugins):
    usage = make_usage(plugins)
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
    scope_group.add_option("-x", "--starred", dest="scope_starred",
                           default=False, action="store_true",
                           help="processing starred topics only")
    parser.add_option_group(scope_group)

    # Plugins Options
    for module in plugins.values():
        if hasattr(module, 'add_option_group'):
            module.add_option_group(parser)

    # Other Options
    other_group = OptionGroup(parser, "Other Options")
    other_group.add_option("-w", "--workers", dest="workers",
                           default=1, type=int,
                           help="number of workers [default: %default]")
    other_group.add_option("-o", "--output", dest="output",
                           default="simple://", help="output uri")
    other_group.add_option("-n", "--count", dest="count",
                           default=200,
                           help="the number of topics "
                           "that can be read at once [default: %default]")
    other_group.add_option("-c", "--coding", dest="coding", default="utf8",
                           help="output coding [default: %default]")
    other_group.add_option("-v", "--verbose", action="store_true",
                           dest="verbose", default=False,
                           help="verbose output")
    other_group.add_option("-h", "--help", action="help")
    parser.add_option_group(other_group)

    return parser.parse_args()


class Worker(Thread):

    """docstring for Worker"""
    def __init__(self, tasks):
        super(Worker, self).__init__()
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, arg, kwd, attempt = self.tasks.get()
            try:
                func(*arg, **kwd)
            except Exception as err:
                print(err)
                if attempt < 3:
                    print("Try again ...", attempt)
                    self.tasks.put((func, arg, kwd, attempt + 1))
                else:
                    print("Failed after ", attempt, "attempts")
            finally:
                self.tasks.task_done()


class ThreadPool:

    def __init__(self, num_threads):
        self.tasks = Queue()
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kargs, 0))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()


def fetch_subscription(g, writer, subscription, options):
    subscription_url = subscription['id'].encode(options.coding)[5:]
    for post in g.posts(subscription_url, options.count):
        writer.put_all(subscription, post)


def main(options, args, plugins):
    if options.verbose:
        root_logger.setLevel(logging.DEBUG)
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
            for post in g.posts(subscription_url, options.count):
                plugin_writer.put_topic(subscription_url, post)

        elif options.scope_starred:
            for post in g.starred(options.count):
                plugin_writer.put_starred(post)

        elif options.scope_all:
            num_workers = 1
            if getattr(plugin_output, 'support_threads', False):
                num_workers = options.workers
            else:
                message = "plugin {0} doesn't support threading: "
                message += "option -w will be ignored"
                if options.cmd_backup:
                    print(message.format(plugin_output.plugin_type))

            pool = ThreadPool(num_workers)
            pool.add_task(map, lambda item: plugin_writer.put_starred(item),
                          g.starred(options.count))
            for subscription in g.subscriptions:
                pool.add_task(fetch_subscription,
                              g, plugin_writer, subscription, options)
            pool.wait_completion()


def entry_main():
    plugins = get_plugins()
    options, args = get_params(plugins)
    check_result = check_params(options)
    if check_result:
        print(check_result)
        sys.exit(1)
    else:
        main(options, args, plugins)


if __name__ == '__main__':
    entry_main()
