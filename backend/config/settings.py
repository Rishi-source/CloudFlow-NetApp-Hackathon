from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    mongodb_url: str
    mongodb_database: str
    redis_url: str
    kafka_bootstrap_servers: str
    kafka_topic_access: str
    kafka_topic_migration: str
    kafka_topic_metrics: str
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    aws_s3_bucket: str = ""
    azure_storage_connection_string: str = ""
    azure_container_name: str = ""
    google_application_credentials: str = ""
    gcp_bucket_name: str = ""
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440
    encryption_key: str
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000"
    ml_model_path: str = "./models"
    ml_training_interval: int = 21600
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    alert_from_email: str = "alerts@cloudflow.io"
    dashboard_url: str = "http://localhost:3000"
    migration_max_retries: int = 3
    migration_retry_delay: int = 5
    migration_retry_multiplier: int = 2
    conflict_resolution_strategy: str = "last_write_wins"
    transaction_log_enabled: bool = True
    performance_metrics_enabled: bool = True
    metrics_collection_interval: int = 60
    deduplication_enabled: bool = True
    compression_enabled: bool = True
    compression_level: int = 6
    multi_region_enabled: bool = True
    default_region: str = "us-east-1"
    backup_enabled: bool = True
    backup_interval: int = 3600
    backup_retention_days: int = 7
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

settings = Settings()
