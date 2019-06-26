import os
from shutil import copyfile
from typing import List
from .base import BaseRemote

__author__ = 'Akshat Bajaj'
__date__ = '2019/02/18'

class Local(BaseRemote):
    """
    Example remote that is primarily used for unit testing.
    Push and pulls from a local directory.
    """

    def file_exists_on_remote(self, path_to_remote: str, relative_path_to_remote_file: str, append_to: bool = True) -> bool:
        path_to_remote_file = os.path.join(path_to_remote, relative_path_to_remote_file)
        return self.file_exists_locally(path_to_remote_file, append_to)

    def pull_file(self, what_to_pull: str, key: str, path_to_remote: str, relative_path_to_remote_file: str, path_to_local_file: str) -> str:
        path_to_remote_file = os.path.join(path_to_remote, relative_path_to_remote_file)
        copyfile(path_to_remote_file, path_to_local_file)
        return "info: " + key + " pulled successfully"

    def push_file(self, what_to_push: str, key: str, path_to_remote: str, relative_path_to_remote_file: str, path_to_local_file: str) -> str:
        path_to_remote_file = os.path.join(path_to_remote, relative_path_to_remote_file)
        copyfile(path_to_local_file, path_to_remote_file)
        return "info: " + key + " pushed successfully"

    def list_files(self, path_to_remote: str, project_name: str) -> List[str]:
        os.makedirs(os.path.join(path_to_remote, project_name), exist_ok=True)
        path_to_remote_files = os.path.join(path_to_remote, project_name)
        remote_files = os.listdir(path_to_remote_files)
        return remote_files
