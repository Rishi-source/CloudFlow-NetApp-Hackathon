from azure.storage.blob import BlobServiceClient
from .cloud_adapter import CloudAdapter
from config.settings import settings

class AzureHandler(CloudAdapter):
    def __init__(self):
        self.blob_service = BlobServiceClient.from_connection_string(settings.azure_storage_connection_string)
        self.container_name = settings.azure_container_name
    async def upload(self, file_path: str, destination: str) -> str:
        blob_client = self.blob_service.get_blob_client(container=self.container_name, blob=destination)
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        return f"azure://{self.container_name}/{destination}"
    async def download(self, source_url: str, local_path: str) -> bool:
        blob_name = source_url.replace(f"azure://{self.container_name}/", "")
        blob_client = self.blob_service.get_blob_client(container=self.container_name, blob=blob_name)
        with open(local_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        return True
    async def delete(self, url: str) -> bool:
        blob_name = url.replace(f"azure://{self.container_name}/", "")
        blob_client = self.blob_service.get_blob_client(container=self.container_name, blob=blob_name)
        blob_client.delete_blob()
        return True
    async def list_objects(self, prefix: str) -> list:
        container_client = self.blob_service.get_container_client(self.container_name)
        blobs = container_client.list_blobs(name_starts_with=prefix)
        return [{'key': blob.name, 'size': blob.size} for blob in blobs]
    async def get_metadata(self, url: str) -> dict:
        blob_name = url.replace(f"azure://{self.container_name}/", "")
        blob_client = self.blob_service.get_blob_client(container=self.container_name, blob=blob_name)
        properties = blob_client.get_blob_properties()
        return {'size': properties.size, 'last_modified': properties.last_modified}
    def set_storage_tier(self, blob_name: str, tier: str):
        tier_map = {"hot": "Hot", "warm": "Cool", "cold": "Archive"}
        blob_client = self.blob_service.get_blob_client(container=self.container_name, blob=blob_name)
        blob_client.set_standard_blob_tier(tier_map[tier])
