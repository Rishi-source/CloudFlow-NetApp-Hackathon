from google.cloud import storage
from .cloud_adapter import CloudAdapter
from config.settings import settings
import os

class GCPHandler(CloudAdapter):
    def __init__(self):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.google_application_credentials
        self.client = storage.Client()
        self.bucket = self.client.bucket(settings.gcp_bucket_name)
    async def upload(self, file_path: str, destination: str) -> str:
        blob = self.bucket.blob(destination)
        blob.upload_from_filename(file_path)
        return f"gs://{settings.gcp_bucket_name}/{destination}"
    async def download(self, source_url: str, local_path: str) -> bool:
        blob_name = source_url.replace(f"gs://{settings.gcp_bucket_name}/", "")
        blob = self.bucket.blob(blob_name)
        blob.download_to_filename(local_path)
        return True
    async def delete(self, url: str) -> bool:
        blob_name = url.replace(f"gs://{settings.gcp_bucket_name}/", "")
        blob = self.bucket.blob(blob_name)
        blob.delete()
        return True
    async def list_objects(self, prefix: str) -> list:
        blobs = self.client.list_blobs(self.bucket, prefix=prefix)
        return [{'key': blob.name, 'size': blob.size} for blob in blobs]
    async def get_metadata(self, url: str) -> dict:
        blob_name = url.replace(f"gs://{settings.gcp_bucket_name}/", "")
        blob = self.bucket.blob(blob_name)
        blob.reload()
        return {'size': blob.size, 'last_modified': blob.updated}
    def set_storage_tier(self, blob_name: str, tier: str):
        class_map = {"hot": "STANDARD", "warm": "NEARLINE", "cold": "COLDLINE"}
        blob = self.bucket.blob(blob_name)
        blob.update_storage_class(class_map[tier])
