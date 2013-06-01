#!/usr/bin/env python
# coding=utf-8
from setuptools import setup
from grbackup import __version__, __description__, requires


setup(name='grbackup',
      version=__version__,
      description=__description__,
      author='wistful',
      packages=['grbackup', 'grbackup.grb_plugins'],
      install_requires=requires,
      entry_points={
      'console_scripts': [
          'grbackup = grbackup.grbackup:entry_main'
      ]},
      )
