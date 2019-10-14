import os
import re

from google.cloud import storage
from google.cloud.exceptions import NotFound
from google.oauth2 import service_account

from .storage_driver import StorageDriver
from .util import get_surround_config, join_path, normalize_path

class GCloudStorageDriver(StorageDriver):
    def __init__(self, url):
        super().__init__(url)

        config = get_surround_config()
        json_path = None

        if config.get_path("experiment.credentials.google"):
            json_path = config.get_path("experiment.credentials.google")
        elif 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
            json_path = os.environ['GOOGLE_APPLICATION_CREDENTIALS']

        if not json_path:
            raise Exception('No credentials provided for Google Cloud Stoage bucket!')

        creds = service_account.Credentials.from_service_account_file(json_path, scopes=['https://www.googleapis.com/auth/cloud-platform'])
        self.client = storage.Client(credentials=creds)

        pattern_match = re.match(r"^gs://([a-z0-9\-_\.]+)[/\\]{,1}(.*)$", url)

        if pattern_match:
            self.bucket_name = pattern_match.group(1)
            self.base_path = pattern_match.group(2)

            try:
                self.bucket = self.client.get_bucket(self.bucket_name)
            except Exception:
                raise Exception("Failed to find the bucket specified!")
        else:
            raise ValueError("Unexpected URL format!\nShould be formatted as gs://bucket-name")

    def pull(self, remote_path, local_path=None, override_ok=False):
        blob = self.bucket.blob(join_path(self.base_path, remote_path))

        data = None
        try:
            data = blob.download_as_string()
        except NotFound:
            raise FileNotFoundError("That file doesn't exist")

        if local_path:
            if not override_ok and os.path.exists(local_path):
                raise FileExistsError("File already exists at pull location!")

            with open(local_path, "wb+") as f:
                f.write(data)

            return True

        return data

    def push(self, remote_path, local_path=None, bytes_data=None, override_ok=True):
        blob = self.bucket.blob(join_path(self.base_path, remote_path))

        if not override_ok and blob.exists():
            raise FileExistsError("This file already exists")

        if not local_path and not bytes_data:
            raise ValueError("local_path or bytes_data need to have values!")

        if local_path and bytes_data:
            raise ValueError("local_path and bytes_data are mutually exclusive!")

        if local_path:
            if not os.path.exists(local_path):
                raise FileNotFoundError("Could not find the file to push!")

            blob.upload_from_filename(local_path)
        else:
            blob.upload_from_string(bytes_data, content_type="application/octet-stream")

    def delete(self, remote_path):
        blob = self.bucket.blob(join_path(self.base_path, remote_path))

        try:
            blob.delete()
        except NotFound:
            remote_path = normalize_path(remote_path)
            blobs = self.client.list_blobs(self.bucket, prefix=remote_path)

            is_empty = True
            for b in blobs:
                b.delete()
                is_empty = False

            if is_empty:
                raise FileNotFoundError("Could not find the file/folder to delete!")

    def exists(self, remote_path):
        blob = self.bucket.blob(join_path(self.base_path, remote_path))
        file_exists = blob.exists()

        if not file_exists:
            blobs = iter(self.client.list_blobs(self.bucket, prefix=remote_path))

            try:
                next(blobs)
                return True
            except Exception:
                return False

        return file_exists

    def get_files(self, base_url=None):
        if base_url:
            base_url = normalize_path(base_url)

        blobs = self.client.list_blobs(self.bucket, prefix=base_url)
        blobs = [blob.name[len(base_url):] for blob in blobs]
        blobs = [name if name[0] != "/" else name[1:] for name in blobs]

        return blobs
