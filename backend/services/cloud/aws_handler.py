import boto3
import os
from botocore.exceptions import ClientError
from .cloud_adapter import CloudAdapter
from config.settings import settings

class AWSHandler(CloudAdapter):
    def __init__(self):
        self.s3_client = boto3.client('s3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        self.bucket_name = settings.aws_s3_bucket
    async def upload(self, file_path: str, destination: str) -> str:
        try:
            file_size = os.path.getsize(file_path)
            if file_size > 100 * 1024 * 1024:
                self._multipart_upload(file_path, destination)
            else:
                self.s3_client.upload_file(file_path, self.bucket_name, destination)
            return f"s3://{self.bucket_name}/{destination}"
        except ClientError as e:
            raise Exception(f"AWS upload failed: {str(e)}")
    async def download(self, source_url: str, local_path: str) -> bool:
        key = source_url.replace(f"s3://{self.bucket_name}/", "")
        self.s3_client.download_file(self.bucket_name, key, local_path)
        return True
    async def delete(self, url: str) -> bool:
        key = url.replace(f"s3://{self.bucket_name}/", "")
        self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
        return True
    async def list_objects(self, prefix: str) -> list:
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
        return [{'key': obj['Key'], 'size': obj['Size']} for obj in response.get('Contents', [])]
    async def get_metadata(self, url: str) -> dict:
        key = url.replace(f"s3://{self.bucket_name}/", "")
        response = self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
        return {'size': response['ContentLength'], 'last_modified': response['LastModified']}
    def set_storage_tier(self, key: str, tier: str):
        storage_class_map = {"hot": "STANDARD", "warm": "STANDARD_IA", "cold": "GLACIER"}
        self.s3_client.copy_object(
            Bucket=self.bucket_name,
            CopySource={'Bucket': self.bucket_name, 'Key': key},
            Key=key,
            StorageClass=storage_class_map[tier]
        )
    def _multipart_upload(self, file_path: str, destination: str):
        multipart = self.s3_client.create_multipart_upload(
            Bucket=self.bucket_name,
            Key=destination,
            ServerSideEncryption='AES256'
        )
        parts = []
        part_size = 100 * 1024 * 1024
        with open(file_path, 'rb') as f:
            part_number = 1
            while True:
                data = f.read(part_size)
                if not data:
                    break
                response = self.s3_client.upload_part(
                    Bucket=self.bucket_name,
                    Key=destination,
                    PartNumber=part_number,
                    UploadId=multipart['UploadId'],
                    Body=data
                )
                parts.append({'PartNumber': part_number, 'ETag': response['ETag']})
                part_number += 1
        self.s3_client.complete_multipart_upload(
            Bucket=self.bucket_name,
            Key=destination,
            UploadId=multipart['UploadId'],
            MultipartUpload={'Parts': parts}
        )
