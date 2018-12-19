"""
Python package definition for Surround
"""
import os
import sys

from setuptools import setup, find_packages
from setuptools.command.install import install


# circleci.py version
VERSION = "0.1.0"

class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'Verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('VERSION_TAG')

        if tag != VERSION:
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, VERSION
            )
            sys.exit(info)

setup(name='surround',
      version=VERSION,
      description='Surround is a framework for serving machine learning pipelines in Python.',
      url='http://github.com/dstil/surround',
      author='Scott Barnett',
      author_email='scott.barnett@deakin.edu.au',
      packages=['surround'],
      test_suite="surround.tests",
      zip_safe=False,
      cmdclass={
        'verify': VerifyVersionCommand,
      }
)
