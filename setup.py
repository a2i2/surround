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
      packages=['surround', 'templates', 'surround.remote', 'surround.split', 'surround.visualise', 'surround.data', 'surround.data.cli', 'surround.configuration', 'surround.experiment', 'surround.experiment.web'],
      test_suite='surround.tests',
      entry_points={
          'console_scripts': [
              'surround=surround.cli:main',
          ],
      },
      zip_safe=False,
      install_requires=INSTALL_REQUIRES)
