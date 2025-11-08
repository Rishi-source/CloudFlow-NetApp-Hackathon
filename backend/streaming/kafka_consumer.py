from kafka import KafkaConsumer
import json
import logging
from datetime import datetime
from config.settings import settings
import threading

class CloudFlowKafkaConsumer:
    def __init__(self, db, redis_client):
        self.db = db
        self.redis = redis_client
        self.consumer = None
        self.running = False
        self._connect()
    
    def _connect(self):
        try:
            self.consumer = KafkaConsumer(
                settings.kafka_topic_access,
                settings.kafka_topic_migration,
                settings.kafka_topic_metrics,
                bootstrap_servers=settings.kafka_bootstrap_servers.split(','),
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                group_id='cloudflow-consumer-group',
                auto_offset_reset='latest'
            )
            logging.info("Kafka consumer connected")
        except Exception as e:
            logging.error(f"Kafka consumer connection failed: {str(e)}")
            self.consumer = None
    
    def start(self):
        if not self.consumer:
            logging.warning("Kafka consumer not available")
            return
        self.running = True
        consumer_thread = threading.Thread(target=self._consume_messages, daemon=True)
        consumer_thread.start()
        logging.info("Kafka consumer started")
    
    def _consume_messages(self):
        while self.running:
            try:
                for message in self.consumer:
                    event = message.value
                    self._process_event(event)
            except Exception as e:
                logging.error(f"Error consuming messages: {str(e)}")
                if self.running:
                    continue
                else:
                    break
    
    def _process_event(self, event: dict):
        event_type = event.get("event_type")
        try:
            if event_type == "data_access":
                self._handle_access_event(event)
            elif event_type == "migration":
                self._handle_migration_event(event)
            elif event_type == "metrics":
                self._handle_metrics_event(event)
        except Exception as e:
            logging.error(f"Error processing event: {str(e)}")
    
    def _handle_access_event(self, event: dict):
        self.db["access_logs"].insert_one({
            "data_object_id": event["data_object_id"],
            "access_type": event["access_type"],
            "latency_ms": event["latency_ms"],
            "location": event["location"],
            "timestamp": datetime.fromisoformat(event["timestamp"]),
            "success": True
        })
        self.db["data_objects"].update_one(
            {"_id": event["data_object_id"]},
            {
                "$inc": {"access_count": 1},
                "$set": {"last_accessed": datetime.utcnow()}
            }
        )
        recent_key = f"recent_access:{event['data_object_id']}"
        self.redis.lpush(recent_key, json.dumps(event))
        self.redis.ltrim(recent_key, 0, 99)
        self.redis.expire(recent_key, 86400)
    
    def _handle_migration_event(self, event: dict):
        job_id = event["job_id"]
        update_data = {
            "status": event["status"],
            "progress_percentage": event["progress"]
        }
        if event["status"] == "completed":
            update_data["end_time"] = datetime.utcnow()
        elif event["status"] == "in_progress" and not self.db["migration_jobs"].find_one({"job_id": job_id, "start_time": {"$exists": True}}):
            update_data["start_time"] = datetime.utcnow()
        self.db["migration_jobs"].update_one(
            {"job_id": job_id},
            {"$set": update_data}
        )
        migration_key = f"migration_status:{job_id}"
        self.redis.set(migration_key, json.dumps(event), ex=3600)
    
    def _handle_metrics_event(self, event: dict):
        metric_key = f"metrics:{event['metric_type']}:{datetime.utcnow().strftime('%Y%m%d%H')}"
        self.redis.lpush(metric_key, json.dumps(event["data"]))
        self.redis.expire(metric_key, 604800)
    
    def stop(self):
        self.running = False
        if self.consumer:
            self.consumer.close()
            logging.info("Kafka consumer stopped")
