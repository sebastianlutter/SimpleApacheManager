#!/usr/bin/env python
#
# Install script based on setuptools and pip
#

import sys
# check if setuptools are available
try:
    from setuptools import setup, find_packages
except ImportError:
    print("Please install python3-setuptools in your operation system. Abort.")
    sys.exit(1)

import re

# get version from SimpleApacheManager.py
version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('sam/SimpleApacheManager.py').read(),
    re.M
    ).group(1)

# load README.md as long description
with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")

setup(name='SimpleApacheManager',
      version=version,
      description='Simple Apache VHost manager providing a CLI written in Python 3',
      long_description = long_descr,
      author='Sebastian Lutter',
      author_email='sebastian@vime-it.de',
      url='https://www.vime-it.de',
      license='GPLv3',
      packages=find_packages(),
      install_requires=[
          'configparser',
          'pip',
          'argparse'
      ],
      entry_points = {
        "console_scripts": ['samcli = sam.SimpleApacheManager:main']
      },
#      package_dir = {'': 'sam'}
#      scripts=['scripts/install.sh']
#      package_data={
#          # If any package contains *.txt or *.rst files, include them:
#          '': ['*.txt', '*.rst'],
#          # And include any *.msg files found in the 'hello' package, too:
#          'hello': ['*.msg'],
#      }
)