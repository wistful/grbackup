#!/usr/bin/env python
# coding=utf-8
import json
from optparse import OptionParser
from greader import GReader


def get_params():
    parser = OptionParser()
    parser.add_option("-e", "--email", dest="email",
                      help="email account", metavar="EMAIL")
    parser.add_option("-p", "--password", dest="pwd",
                      help="account password", metavar="PWD")
    parser.add_option("-o", "--output", dest="output",
                      help="output file", metavar="OUT")

    return parser.parse_args()


if __name__ == '__main__':
    options, args = get_params()
    while not options.email:
        options.email = raw_input("email: ")
    while not options.pwd:
        options.pwd = raw_input("password: ")

    print(options)
    g = GReader(options.email, options.pwd)
    print g.is_auth
    if not(args):
        # print help if args is empty list
        pass
    elif args[0] not in ("b", "s", "t"):
        print ("Unknown command '{0}'".format(args[0]))
        # print help
    elif args[0].lower() == "b":
        # backup
        pass
    elif args[0].lower() == "s":
        for subscription in g.subscriptions:
            print(subscription['title'], subscription['id'][5:])
    else:
        # args[0].lower() == "t"
        if len(args) < 2:
            print("Please specify rss url as a second argument")
        else:
            subscription_url = args[1]
            print("\nfeed: {url}\n\n".format(url=subscription_url))
            posts = []
            for i, post in enumerate(g.posts(subscription_url)):
                posts.append(post)
                date = {'updated': post['updated'],
                        'published': post['published']}
                url = post['alternate'][0]['href']
                title = post['title']
                print('{index}, {title}, {url}'.format(
                      index=i, date=date, title=title.encode('utf8'), url=url))
            open(options.output, 'w').write(json.dumps(posts))
