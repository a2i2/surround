import logging
from abc import abstractmethod, ABC

LOGGER = logging.getLogger(__name__)

class StorageDriver(ABC):
    def __init__(self, url):
        self.url = url
        self.is_cloud = False

    @abstractmethod
    def pull(self, remote_path, local_path=None, override_ok=False):
        """
        Pulls a file from the storage location onto the local disk (if local_path provided),
        otherwise the file's contents will be returned (in bytes).

        :param remote_path: path to the file in storage
        :type remote_path: str
        :param local_path: path to pull the file to
        :type local_path: str
        :param override_ok: when pulling to disk, is it okay to override if already exists
        :type override_ok: bool
        :returns: when local_path is None, the contents of the file
        :rtype: bytes
        """

    @abstractmethod
    def push(self, remote_path, local_path=None, bytes_data=None, override_ok=False):
        """
        Push a file to the storage location from the local disk or directly from memory (via bytes).

        :param remote_path: destination path on the remote storage
        :type remote_path: str
        :param local_path: path to the file being pushed from local disk
        :type local_path: str
        :param bytes_data: data to push from memory
        :type bytes_data: bytes
        :param override_ok: when pushing to storage, is it okay to override if it already exists
        :type override_ok: bool
        """

    @abstractmethod
    def delete(self, remote_path):
        """
        Delete a file from the storage location

        :param remote_path: path to the file on the storage location
        :type remote_path: str
        """

    @abstractmethod
    def get_files(self, base_url=None):
        """
        Get a list of all the files in the storage location

        :param base_url: filter the results by sub-directories
        :type base_url: str
        :returns: list of file paths (empty list if no files)
        :rtype: list
        """
