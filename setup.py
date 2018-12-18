"""
Python package definition for Surround
"""

from setuptools import setup, find_packages
setup(name='surround',
      version='0.1.0',
      description='Surround is a framework for serving machine learning pipelines in Python.',
      url='http://github.com/dstil/surround',
      author='Scott Barnett',
      author_email='scott.barnett@deakin.edu.au',
      packages=['surround'],
      test_suite="surround.tests",
      zip_safe=False)
