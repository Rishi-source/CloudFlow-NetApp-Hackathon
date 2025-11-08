from sklearn.ensemble import IsolationForest
import numpy as np
from datetime import datetime, timedelta

class AnomalyDetector:
    def __init__(self, contamination=0.1):
        self.access_model = IsolationForest(contamination=contamination, random_state=42)
        self.cost_model = IsolationForest(contamination=contamination, random_state=42)
        self.latency_model = IsolationForest(contamination=contamination, random_state=42)
        self.trained = False
    def train_access_model(self, access_logs):
        if not access_logs or len(access_logs) < 10:
            return False
        features = self._extract_access_features(access_logs)
        self.access_model.fit(features)
        self.trained = True
        return True
    def train_cost_model(self, cost_data):
        if not cost_data or len(cost_data) < 10:
            return False
        features = np.array([[d['daily_cost'], d['change_rate']] for d in cost_data])
        self.cost_model.fit(features)
        return True
    def train_latency_model(self, latency_logs):
        if not latency_logs or len(latency_logs) < 10:
            return False
        features = np.array([[log['latency_ms'], log['request_rate']] for log in latency_logs])
        self.latency_model.fit(features)
        return True
    def detect_access_anomaly(self, data_object_id, db):
        if not self.trained:
            return {"is_anomaly": False, "reason": "Model not trained"}
        recent_logs = list(db["access_logs"].find({"data_object_id": data_object_id}).sort("timestamp", -1).limit(100))
        if not recent_logs:
            return {"is_anomaly": False, "reason": "No data"}
        features = self._extract_access_features([recent_logs[-1]])
        anomaly_score = self.access_model.decision_function(features)[0]
        is_anomaly = self.access_model.predict(features)[0] == -1
        severity = self._calculate_severity(anomaly_score)
        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": float(anomaly_score),
            "severity": severity,
            "anomaly_type": self._classify_access_anomaly(recent_logs),
            "recommendation": self._generate_access_recommendation(recent_logs) if is_anomaly else None
        }
    def detect_cost_anomaly(self, current_cost, historical_costs):
        if len(historical_costs) < 2:
            return {"is_anomaly": False}
        change_rate = (current_cost - historical_costs[-1]) / historical_costs[-1] if historical_costs[-1] > 0 else 0
        features = np.array([[current_cost, change_rate]])
        anomaly_score = self.cost_model.decision_function(features)[0]
        is_anomaly = self.cost_model.predict(features)[0] == -1
        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": float(anomaly_score),
            "severity": "high" if change_rate > 0.3 else "medium",
            "change_rate": float(change_rate),
            "recommendation": f"Cost increased by {change_rate*100:.1f}%. Review expensive objects." if is_anomaly else None
        }
    def detect_latency_spike(self, current_latency, request_rate, historical_data):
        if not historical_data or len(historical_data) < 5:
            return {"is_anomaly": False}
        features = np.array([[current_latency, request_rate]])
        anomaly_score = self.latency_model.decision_function(features)[0]
        is_anomaly = self.latency_model.predict(features)[0] == -1
        avg_latency = np.mean([d['latency_ms'] for d in historical_data])
        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": float(anomaly_score),
            "severity": "critical" if current_latency > avg_latency * 3 else "medium",
            "avg_latency": float(avg_latency),
            "current_latency": float(current_latency),
            "recommendation": "Consider tier upgrade or migration" if is_anomaly else None
        }
    def _extract_access_features(self, logs):
        features = []
        for log in logs:
            hour = log.get('timestamp', datetime.now()).hour if isinstance(log.get('timestamp'), datetime) else 12
            features.append([
                log.get('latency_ms', 0),
                1 if log.get('access_type') == 'write' else 0,
                hour,
                log.get('bytes_transferred', 0) / 1024
            ])
        return np.array(features)
    def _calculate_severity(self, score):
        if score < -0.7:
            return "critical"
        elif score < -0.4:
            return "high"
        elif score < -0.2:
            return "medium"
        return "low"
    def _classify_access_anomaly(self, logs):
        if not logs:
            return "unknown"
        recent_count = len([l for l in logs if (datetime.now() - l['timestamp']).seconds < 3600])
        if recent_count > 50:
            return "access_surge"
        elif all(l.get('access_type') == 'write' for l in logs[:5]):
            return "excessive_writes"
        return "unusual_pattern"
    def _generate_access_recommendation(self, logs):
        anomaly_type = self._classify_access_anomaly(logs)
        recommendations = {
            "access_surge": "Consider migrating to hot tier for better performance",
            "excessive_writes": "Review write patterns and optimize data structure",
            "unusual_pattern": "Investigate access source and validate legitimacy"
        }
        return recommendations.get(anomaly_type, "Monitor closely")
