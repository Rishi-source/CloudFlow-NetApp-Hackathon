from abc import ABC, abstractmethod
from typing import List
import hashlib

class CloudAdapter(ABC):
    @abstractmethod
    async def upload(self, file_path: str, destination: str) -> str:
        pass
    @abstractmethod
    async def download(self, source_url: str, local_path: str) -> bool:
        pass
    @abstractmethod
    async def delete(self, url: str) -> bool:
        pass
    @abstractmethod
    async def list_objects(self, prefix: str) -> List[dict]:
        pass
    @abstractmethod
    async def get_metadata(self, url: str) -> dict:
        pass
    @abstractmethod
    def set_storage_tier(self, key: str, tier: str):
        pass
    def calculate_checksum(self, file_path: str) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
