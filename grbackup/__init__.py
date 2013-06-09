#!/usr/bin/env python
# coding=utf-8

__version__ = '1.1'
__description__ = 'Utilite to backup items from Google Reader'
requires = [
    'pymongo>=2.4',
    'redis'
]
README = """grbackup is a Python library used
to save all items from your Google Reader account into different places.

Usage
=====

::

   list subscriptions: grbackup -e email@gmail.com -p password -ls
   list topics: grbackup -e email@gmail.com -p password -lt http://feed.com
   list starred: grbackup -e email@gmail.com -p password -lx
   list all items: grbackup -e email@gmail.com -p password -la

   backup subscriptions: grbackup -e email@gmail.com -p password -bs -o json:/tmp/subscriptions.json
   backup topics: grbackup -e email@gmail.com -p password -bt http://myfeed.com -o json:/tmp/myfeed.json
   backup starred into MongoDB: grbackup -e email@gmail.com -p password -bx -o mongodb://localhost:27017
   backup all items into Redis: grbackup -e email@gmail.com -p password -ba -o redis://localhost:6379/3
"""
