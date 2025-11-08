import gzip
from typing import Tuple
from config.settings import settings

class Compressor:
    def __init__(self):
        self.enabled = settings.compression_enabled
        self.level = settings.compression_level
    def compress(self, data: bytes) -> Tuple[bytes, float]:
        if not self.enabled:
            return data, 0.0
        compressed = gzip.compress(data, compresslevel=self.level)
        original_size = len(data)
        compressed_size = len(compressed)
        ratio = ((original_size - compressed_size) / original_size * 100) if original_size > 0 else 0.0
        return compressed, round(ratio, 2)
    def decompress(self, data: bytes) -> bytes:
        if not self.enabled:
            return data
        return gzip.decompress(data)
    def should_compress(self, file_size: int, file_extension: str) -> bool:
        if not self.enabled:
            return False
        skip_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.mp4', '.zip', '.gz', '.bz2'}
        return file_extension.lower() not in skip_extensions and file_size > 1024

compressor = Compressor()
