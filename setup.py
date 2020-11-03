"""
Python package definition for Surround
"""
import os

from setuptools import setup

# Collect version from repo tag
VERSION = os.getenv('VERSION_TAG')
with open("requirements.txt") as f:
    INSTALL_REQUIRES = f.read().split("\n")

setup(name='surround',
      version=VERSION,
      description='Surround is a framework for serving machine learning pipelines in Python.',
      url='http://github.com/dstil/surround',
      author='Scott Barnett',
      author_email='scott.barnett@deakin.edu.au',
      include_package_data=True,
      packages=[
          'surround',
          'templates',
          'surround.remote',
          'surround.split',
          'surround.visualise',
          'surround.data',
          'surround.configuration',
          'surround.experiment',
          'surround.experiment.web',
          'surround.checkers'
      ],
      test_suite='surround.tests',
      license="BSD-3-Clause License",
      zip_safe=False,
      install_requires=INSTALL_REQUIRES)
