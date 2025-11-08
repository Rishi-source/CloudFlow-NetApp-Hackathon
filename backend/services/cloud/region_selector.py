from typing import Dict, List
from config.settings import settings

class RegionSelector:
    def __init__(self):
        self.enabled = settings.multi_region_enabled
        self.default_region = settings.default_region
        self.regions = {"aws": ["us-east-1", "us-west-2", "eu-west-1", "ap-south-1"], "azure": ["eastus", "westus2", "westeurope", "southeastasia"], "gcp": ["us-central1", "us-west1", "europe-west1", "asia-south1"]}
        self.latency_map = {"us-east-1": 50, "us-west-2": 80, "eu-west-1": 120, "ap-south-1": 150, "eastus": 55, "westus2": 85, "westeurope": 125, "southeastasia": 160, "us-central1": 60, "us-west1": 90, "europe-west1": 130, "asia-south1": 155}
    def select_optimal_region(self, provider: str, user_location: str = "us") -> str:
        if not self.enabled:
            return self.default_region
        available_regions = self.regions.get(provider, [self.default_region])
        if user_location == "us":
            return available_regions[0] if available_regions else self.default_region
        elif user_location == "eu":
            return next((r for r in available_regions if "eu" in r or "europe" in r), available_regions[0])
        elif user_location == "asia":
            return next((r for r in available_regions if "asia" in r or "ap" in r), available_regions[0])
        return available_regions[0] if available_regions else self.default_region
    def get_estimated_latency(self, region: str) -> int:
        return self.latency_map.get(region, 100)
    def get_all_regions(self, provider: str) -> List[str]:
        return self.regions.get(provider, [self.default_region])

region_selector = RegionSelector()
