import re

from .file_storage_driver import FileStorageDriver
from .gcloud_storage_driver import GCloudStorageDriver

def get_driver_type_from_url(url):
    """
    Return the storage driver type accoriding to the URL provided

    :param url: the url to determine type from
    :type url: str
    :returns: the driver type
    :rtype: type
    """

    if re.match(r'gs://.+', url):
        return GCloudStorageDriver

    return FileStorageDriver
