import schedule
import time
import logging
from datetime import datetime, timedelta
from ml.anomaly_detector import AnomalyDetector
from ml.prediction_engine import PredictionEngine

class ModelTrainer:
    def __init__(self, db):
        self.db = db
        self.anomaly_detector = AnomalyDetector()
        self.prediction_engine = PredictionEngine(db)
        self.training_history = []
    def schedule_training(self, interval_hours=6):
        schedule.every(interval_hours).hours.do(self.retrain_all_models)
        logging.info(f"Model training scheduled every {interval_hours} hours")
        while True:
            schedule.run_pending()
            time.sleep(60)
    def retrain_all_models(self):
        logging.info("Starting scheduled model retraining")
        try:
            access_metrics = self._retrain_access_predictor()
            anomaly_metrics = self._retrain_anomaly_detector()
            self._log_training_results(access_metrics, anomaly_metrics)
            return {"status": "success", "timestamp": datetime.utcnow().isoformat()}
        except Exception as e:
            logging.error(f"Training failed: {str(e)}")
            return {"status": "failed", "error": str(e)}
    def _retrain_access_predictor(self):
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        logs = list(self.db["access_logs"].find({"timestamp": {"$gte": cutoff_date}}))
        if len(logs) < 100:
            return {"status": "skipped", "reason": "insufficient_data"}
        success = self.prediction_engine.train_model(logs)
        return {"status": "completed", "samples": len(logs), "success": success}
    def _retrain_anomaly_detector(self):
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        access_logs = list(self.db["access_logs"].find({"timestamp": {"$gte": cutoff_date}}))
        if len(access_logs) < 50:
            return {"status": "skipped", "reason": "insufficient_data"}
        access_success = self.anomaly_detector.train_access_model(access_logs)
        cost_data = self._prepare_cost_data()
        cost_success = self.anomaly_detector.train_cost_model(cost_data) if cost_data else False
        latency_data = self._prepare_latency_data()
        latency_success = self.anomaly_detector.train_latency_model(latency_data) if latency_data else False
        return {
            "status": "completed",
            "access_model": access_success,
            "cost_model": cost_success,
            "latency_model": latency_success
        }
    def _prepare_cost_data(self):
        pipeline = [
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                "daily_cost": {"$sum": "$cost_per_month"}
            }},
            {"$sort": {"_id": 1}},
            {"$limit": 60}
        ]
        result = list(self.db["data_objects"].aggregate(pipeline))
        if len(result) < 10:
            return None
        cost_data = []
        for i, doc in enumerate(result):
            change_rate = 0
            if i > 0:
                prev_cost = result[i-1]['daily_cost']
                change_rate = (doc['daily_cost'] - prev_cost) / prev_cost if prev_cost > 0 else 0
            cost_data.append({"daily_cost": doc['daily_cost'], "change_rate": change_rate})
        return cost_data
    def _prepare_latency_data(self):
        cutoff = datetime.utcnow() - timedelta(days=7)
        pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff}}},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d %H", "date": "$timestamp"}},
                "latency_ms": {"$avg": "$latency_ms"},
                "request_rate": {"$sum": 1}
            }},
            {"$limit": 168}
        ]
        result = list(self.db["access_logs"].aggregate(pipeline))
        return [{"latency_ms": r['latency_ms'], "request_rate": r['request_rate']} for r in result] if len(result) >= 10 else None
    def _log_training_results(self, access_metrics, anomaly_metrics):
        training_record = {
            "timestamp": datetime.utcnow(),
            "access_predictor": access_metrics,
            "anomaly_detector": anomaly_metrics
        }
        self.training_history.append(training_record)
        if len(self.training_history) > 100:
            self.training_history = self.training_history[-100:]
        logging.info(f"Training completed: {training_record}")
    def get_training_history(self):
        return self.training_history[-10:]
