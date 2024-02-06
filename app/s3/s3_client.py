import boto3
import botocore
from datetime import date

class S3Client:
    def __init__(
            self,
            aws_access_key_id: str,
            aws_secret_access_key: str,
            aws_endpoint: str,
            aws_region_name: str
    ):
        self.client = boto3.client(
            service_name='s3',
            endpoint_url=aws_endpoint,
            region_name=aws_region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

        self.resource = boto3.resource(
            service_name='s3',
            endpoint_url=aws_endpoint,
            region_name=aws_region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

    def get_buckets(self):
        buckets = self.client.list_buckets()
        return buckets
    
    def get_file(self, bucket: str, key: str):
        file_object = self.resource.Object(bucket, key)

        return file_object.get()['Body']
    
    def try_upload_file(self, file_path: str, bucket: str, file_name: str):
        today = date.today()
        key = f'{today}/{file_name}'

        try:
            self.client.get_object(Bucket=bucket, Key=key)
        except botocore.exceptions.ClientError as e:
            self.client.upload_file(file_path, bucket, key)

    def get_files_in_bucket(self, bucket: str):
        bucket = self.resource.Bucket(bucket)

        object_summaries = []

        for object_summary in bucket.objects.filter(Prefix=f'{date.today()}'):
            object_summaries.append(object_summary)
        
        return object_summaries
