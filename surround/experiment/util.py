import hashlib
import zipfile

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
