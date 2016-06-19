# -*- coding: utf-8 -*-
from distutils.core import setup

import re
from setuptools import setup

version = re.search(
  '^__version__\s*=\s*"(.*)"',
  open('fwdocker/fwdocker.py').read(),
  re.M
).group(1)


setup(
  name = 'fwdocker',
  packages = ['fwdocker'], # this must be the same as the name above
  version = version,
  entry_points = {
    "console_scripts": ['fwdocker = fwdocker.fwdocker:main']
  },
  description = 'A wrapper/utility to make it easy to use FileWave with Docker',
  author = 'John Clayton',
  author_email = 'johnc@filewave.com',
  url = 'https://github.com/johncclayton/fwdocker', # use the URL to the github repo
  download_url = 'https://github.com/johncclayton/fwdocker/tarball/0.1', # I'll explain this in a second
  keywords = ['filewave', 'docker', 'mdm', 'distribution'], # arbitrary keywords
  classifiers = [],
  license="Apache",
  package_data= {
    # bring in the docker-compose example yml files.
    '': ['*.yml']
  },
  install_requires=[ 'docker-py>=1.8' ]
)
