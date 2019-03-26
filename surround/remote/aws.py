import os
from boto3.session import Session
from .base import BaseRemote

class AWS(BaseRemote):
    ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
    SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

    def __init__(self):
        super().__init__()
        self.session = Session(aws_access_key_id=AWS.ACCESS_KEY, aws_secret_access_key=AWS.SECRET_KEY)

    def get_bucket(self, bucket_name):
        s3 = self.session.resource('s3')
        return s3.Bucket(bucket_name)

    def pull_file(self, what_to_pull, key, file_to_pull, path_to_pulled_file):
        bucket = self.get_bucket(what_to_pull)
        project_name = self.get_project_name()
        bucket.download_file(project_name + '/' + key, what_to_pull + '/' + key)
