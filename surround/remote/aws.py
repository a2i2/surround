import logging
import boto3
from botocore.exceptions import ClientError
from .base import BaseRemote

class AWS(BaseRemote):

    def __init__(self):
        super().__init__()
        self.s3 = boto3.client('s3')

    def file_exists_on_remote(self, path_to_remote, relative_path_to_remote_file, append_to=True):
        bucket = self.get_bucket(path_to_remote)
        if self.bucket_exists(bucket):
            response = self.s3.list_objects_v2(Bucket=bucket)
            for file_ in response['Contents']:
                if relative_path_to_remote_file == file_['Key']:
                    return True
            return False
        return False

    def bucket_exists(self, bucket_name):
        """Determine whether bucket_name exists and the user has permission to access it
        :param bucket_name: Name of the bucket
        :type bucket_name: string
        :return: True if the referenced bucket_name exists, otherwise False
        """
        try:
            self.s3.head_bucket(Bucket=bucket_name)
        except ClientError as e:
            logging.debug(e)
            return False
        return True

    def get_bucket(self, path_to_remote):
        return path_to_remote.split("//")[1]

    def pull_file(self, what_to_pull, key, path_to_remote, relative_path_to_remote_file, path_to_local_file):
        bucket = self.get_bucket(path_to_remote)
        if self.bucket_exists(bucket):
            try:
                self.s3.download_file(bucket, relative_path_to_remote_file, path_to_local_file)
                return "info: " + key + " pulled successfully"
            except ClientError as e:
                if e.response['Error']['Code'] == "404":
                    return "error: " + key + " does not exist"
        return "error: bucket does not exist"

    def push_file(self, what_to_push, key, path_to_remote, relative_path_to_remote_file, path_to_local_file):
        bucket = self.get_bucket(path_to_remote)
        if self.bucket_exists(bucket):
            self.s3.upload_file(path_to_local_file, bucket, relative_path_to_remote_file)
            return "info: " + key + " pushed successfully"
        return "error: bucket does not exist"

    def list_files(self, path_to_remote, project_name):
        bucket = self.get_bucket(path_to_remote)
        if self.bucket_exists(bucket):
            response = self.s3.list_objects_v2(Bucket=bucket)
            files = []
            for file_ in response['Contents']:
                files.append(file_['Key'])
            return files
        return "error: bucket does not exist"
