"""
Python package definition for Surround CLI
"""
from setuptools import setup

# Collect version from VERSION file
with open("VERSION") as version_file:
    VERSION = version_file.read().strip()

with open("requirements.txt") as f:
    INSTALL_REQUIRES = f.read().split("\n")

setup(
    name="surround_cli",
    version=VERSION,
    description="Command line interface for Surround",
    url="https://github.com/a2i2/surround",
    author="Scott Barnett",
    author_email="scott.barnett@deakin.edu.au",
    include_package_data=True,
    packages=[
        "surround_cli",
        "surround_cli.checkers",
        "surround_cli.remote",
        "surround_cli.split",
        "surround_cli.visualise",
        "surround_cli.data",
        "surround_cli.data.cli",
        "templates",
    ],
    entry_points={
        "console_scripts": [
            "surround=surround_cli.cli:main",
        ],
    },
    license="BSD-3-Clause License",
    zip_safe=False,
    install_requires=INSTALL_REQUIRES,
)
