"""
This file is needed to make Python treat this directory as a package
"""

import os

from surround import load_config
from .config import Config


def setup():
    config = load_config(name="config", config_class=Config)
    os.makedirs(config["output_path"], exist_ok=True)


setup()
