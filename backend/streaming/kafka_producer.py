from kafka import KafkaProducer
import json
import logging
from datetime import datetime
from config.settings import settings

class CloudFlowKafkaProducer:
    def __init__(self):
        self.producer = None
        self._connect()
    
    def _connect(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap_servers.split(','),
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=3
            )
            logging.info("Kafka producer connected")
        except Exception as e:
            logging.error(f"Kafka producer connection failed: {str(e)}")
            self.producer = None
    
    def send_access_event(self, data_object_id: str, access_type: str, latency_ms: float, location: str):
        if not self.producer:
            logging.warning("Kafka producer not available")
            return False
        try:
            event = {
                "event_type": "data_access",
                "timestamp": datetime.utcnow().isoformat(),
                "data_object_id": data_object_id,
                "access_type": access_type,
                "latency_ms": latency_ms,
                "location": location
            }
            self.producer.send(settings.kafka_topic_access, value=event)
            self.producer.flush()
            return True
        except Exception as e:
            logging.error(f"Failed to send access event: {str(e)}")
            return False
    
    def send_migration_event(self, job_id: str, status: str, progress: float, data_object_id: str):
        if not self.producer:
            logging.warning("Kafka producer not available")
            return False
        try:
            event = {
                "event_type": "migration",
                "timestamp": datetime.utcnow().isoformat(),
                "job_id": job_id,
                "data_object_id": data_object_id,
                "status": status,
                "progress": progress
            }
            self.producer.send(settings.kafka_topic_migration, value=event)
            self.producer.flush()
            return True
        except Exception as e:
            logging.error(f"Failed to send migration event: {str(e)}")
            return False
    
    def send_metrics_event(self, metric_type: str, metric_data: dict):
        if not self.producer:
            logging.warning("Kafka producer not available")
            return False
        try:
            event = {
                "event_type": "metrics",
                "timestamp": datetime.utcnow().isoformat(),
                "metric_type": metric_type,
                "data": metric_data
            }
            self.producer.send(settings.kafka_topic_metrics, value=event)
            self.producer.flush()
            return True
        except Exception as e:
            logging.error(f"Failed to send metrics event: {str(e)}")
            return False
    
    def close(self):
        if self.producer:
            self.producer.close()
            logging.info("Kafka producer closed")

_kafka_producer = CloudFlowKafkaProducer()

async def send_event(event_type: str, event_data: dict):
    try:
        if not _kafka_producer.producer:
            logging.warning(f"Kafka producer not available for event: {event_type}")
            return False
        
        event = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            **event_data
        }
        
        _kafka_producer.producer.send("cloudflow-events", value=event)
        _kafka_producer.producer.flush()
        logging.info(f"Sent Kafka event: {event_type}")
        return True
    except Exception as e:
        logging.error(f"Failed to send event {event_type}: {str(e)}")
        return False
