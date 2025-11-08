from .cloud_adapter import CloudAdapter
from .aws_handler import AWSHandler
from .azure_handler import AzureHandler
from .gcp_handler import GCPHandler
from .consistency_manager import ConsistencyManager

def get_cloud_adapter(location: str) -> CloudAdapter:
    adapters = {"aws": AWSHandler, "azure": AzureHandler, "gcp": GCPHandler}
    adapter_class = adapters.get(location)
    if not adapter_class:
        raise ValueError(f"Unknown cloud location: {location}")
    return adapter_class()

__all__ = ['CloudAdapter', 'AWSHandler', 'AzureHandler', 'GCPHandler', 'ConsistencyManager', 'get_cloud_adapter']
