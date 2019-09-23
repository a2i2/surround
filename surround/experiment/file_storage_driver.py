import os
import shutil
from .storage_driver import StorageDriver

class FileStorageDriver(StorageDriver):
    def __init__(self, path):
        super().__init__(path)
        os.makedirs(path, exist_ok=True)

    def pull(self, remote_path, local_path=None, override_ok=False):
        if not self.exists(remote_path):
            raise FileNotFoundError("That file doesn't exist")

        path = os.path.join(self.url, remote_path)

        if local_path:
            if not override_ok and os.path.exists(local_path):
                raise Exception("File already exists at pull location!")

            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            shutil.copyfile(path, local_path)
            return True

        with open(path, "rb") as f:
            contents = f.read()
            return contents

    def push(self, remote_path, local_path=None, bytes_data=None, override_ok=False):
        if not override_ok and self.exists(remote_path):
            raise FileExistsError("This file already exists")

        if not local_path and not bytes_data:
            raise ValueError("local_path or bytes_data need to have values!")

        if local_path and bytes_data:
            raise ValueError("local_path and bytes_data are mutually exclusive!")

        path = os.path.join(self.url, remote_path)

        if local_path:
            if not os.path.exists(local_path):
                raise FileNotFoundError("Could not find the file to push!")

            os.makedirs(os.path.dirname(path), exist_ok=True)
            shutil.copyfile(local_path, path)
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb+") as f:
                f.write(bytes_data)

    def delete(self, remote_path):
        if not self.exists(remote_path):
            raise FileNotFoundError("Could not find the file/folder to delete!")

        path = os.path.join(self.url, remote_path)

        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

    def exists(self, remote_path):
        path = os.path.join(self.url, remote_path)
        return os.path.exists(path)

    def get_files(self, base_url=None):
        results = []
        path = self.url

        if base_url:
            path = os.path.join(self.url, base_url)

        for root, _, files in os.walk(path):
            for f in files:
                results.append(os.path.join(root, f))

        return results
