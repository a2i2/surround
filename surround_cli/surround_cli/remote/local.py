import os
from shutil import copyfile
from .base import BaseRemote

__author__ = "Akshat Bajaj"
__date__ = "2019/02/18"


class Local(BaseRemote):
    """
    Example remote that is primarily used for unit testing.
    Push and pulls from a local directory.
    """

    def file_exists_on_remote(
        self, path_to_remote, relative_path_to_remote_file, append_to=True
    ):
        path_to_remote_file = os.path.join(path_to_remote, relative_path_to_remote_file)
        return self.file_exists_locally(path_to_remote_file, append_to)

    def pull_file(
        self,
        what_to_pull,
        key,
        path_to_remote,
        relative_path_to_remote_file,
        path_to_local_file,
    ):
        path_to_remote_file = os.path.join(path_to_remote, relative_path_to_remote_file)
        os.makedirs(os.path.dirname(path_to_local_file), exist_ok=True)
        copyfile(path_to_remote_file, path_to_local_file)
        return "info: " + key + " pulled successfully"

    def push_file(
        self,
        what_to_push,
        key,
        path_to_remote,
        relative_path_to_remote_file,
        path_to_local_file,
    ):
        path_to_remote_file = os.path.join(path_to_remote, relative_path_to_remote_file)
        copyfile(path_to_local_file, path_to_remote_file)
        return "info: " + key + " pushed successfully"

    def list_files(self, path_to_remote, project_name):
        os.makedirs(os.path.join(path_to_remote, project_name), exist_ok=True)
        path_to_remote_files = os.path.join(path_to_remote, project_name)
        remote_files = os.listdir(path_to_remote_files)
        return remote_files
