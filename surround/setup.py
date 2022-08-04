"""
Python package definition for Surround
"""
from setuptools import setup

# Collect version from VERSION file
with open("VERSION") as version_file:
    VERSION = version_file.read().strip()

with open("requirements.txt") as f:
    INSTALL_REQUIRES = f.read().split("\n")

setup(
    name="surround",
    version=VERSION,
    description="Surround is a framework for serving machine learning pipelines in Python.",
    url="https://github.com/a2i2/surround",
    author="Scott Barnett",
    author_email="scott.barnett@deakin.edu.au",
    include_package_data=True,
    packages=["surround"],
    license="BSD-3-Clause License",
    zip_safe=False,
    install_requires=INSTALL_REQUIRES,
)
