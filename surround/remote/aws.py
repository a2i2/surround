import os
import boto3
from .base import BaseRemote

class AWS(BaseRemote):
    ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
    SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

    def __init__(self):
        super().__init__()
        self.s3 = boto3.client('s3', aws_access_key_id=AWS.ACCESS_KEY, aws_secret_access_key=AWS.SECRET_KEY)

    def pull_file(self, what_to_pull, path_to_remote, relative_path_to_remote_file, path_to_local_file):
        self.s3.download_file("surround-" + what_to_pull, relative_path_to_remote_file, path_to_local_file)

    def push_file(self, what_to_push, path_to_remote, relative_path_to_remote_file, path_to_local_file):
        self.s3.upload_file(path_to_local_file, "surround-" + what_to_push, relative_path_to_remote_file)
