import os
import hashlib
import zipfile
import logging

from pathlib import Path
from ..config import Config
from ..configuration import cli as config_cli
from .file_storage_driver import FileStorageDriver

def get_driver_type_from_url(url):
    """
    Return the storage driver type accoriding to the URL provided

    :param url: the url to determine type from
    :type url: str
    :returns: the driver type
    :rtype: type
    """

    return FileStorageDriver


def get_surround_config():
    config = Config(auto_load=False)
    local_config = Config(auto_load=True)

    global_config_path = os.path.join(Path.home(), ".surround", "config.yaml")
    local_config_path = os.path.join(local_config["project_root"], ".surround", "config.yaml")

    global_exists = os.path.exists(global_config_path)
    local_exists = os.path.exists(local_config_path)

    # Load the configuration file from the global surround path
    if global_exists:
        config.read_config_files([global_config_path])

    # Load the configuration file from the project surround path
    if local_exists:
        config.read_config_files([local_config_path])

    # If neither exist or we don't have the required property, setup the configuration
    if not global_exists and (not local_exists or not config.get_path("experiment.url")):
        logger = logging.getLogger(__name__)
        logger.info("Setting up global configuration...")

        if not config.get_path("user.name"):
            logger.info("No username or email have been set in your configuration!")
            logger.info("To set your name and email use the following commands:")
            logger.info("$ surround config user.name John Doe")
            logger.info("$ surround config user.email john.doe@email.com\n")

        config_cli.update_required_fields(config, global_config_path, answers={
            'user.name': 'Unknown',
            'user.email': 'Unknown'
        }, verbose=False)

    return config

def hash_zip(path, skip_files=None):
    sha1 = hashlib.sha1()
    block_size = 256 * 1024 * 1024

    with zipfile.ZipFile(path) as zipf:
        for name in zipf.namelist():
            if skip_files and name in skip_files:
                continue

            with zipf.open(name) as f:
                while True:
                    data = f.read(block_size)

                    if not data:
                        break

                    sha1.update(data)

    return sha1.hexdigest()
