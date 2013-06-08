#!/usr/bin/env python
# coding=utf-8

from setuptools import setup
from grbackup import __version__, __description__, requires, README


setup(name='grbackup',
      version=__version__,
      description=__description__,
      author='wistful',
      author_email='wst.public.mail@gmail.com',
      long_description=README,
      url="https://bitbucket.org/wistful/grbackup",
      license="MIT License",
      packages=['grbackup', 'grbackup.grb_plugins'],
      install_requires=requires,
      entry_points={
      'console_scripts': [
          'grbackup = grbackup.grbackup:entry_main'
      ]},
      platforms=["Unix,"],
      keywords="greader, backup",
      test_suite='tests',
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 2 :: Only",
          "Topic :: System :: Archiving :: Backup",
          "Topic :: Utilities"
      ],
      )
