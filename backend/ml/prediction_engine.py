import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import logging
from datetime import datetime, timedelta
from typing import Dict, Tuple
import os

class MLPredictionEngine:
    def __init__(self, db, model_path: str):
        self.db = db
        self.model_path = model_path
        self.tier_model = None
        self.location_model = None
        self.scaler = StandardScaler()
        self.tier_mapping = {"hot": 0, "warm": 1, "cold": 2}
        self.reverse_tier_mapping = {v: k for k, v in self.tier_mapping.items()}
        self.location_mapping = {"on-premise": 0, "aws": 1, "azure": 2, "gcp": 3}
        self.reverse_location_mapping = {v: k for k, v in self.location_mapping.items()}
        self._ensure_model_dir()
    
    def _ensure_model_dir(self):
        os.makedirs(self.model_path, exist_ok=True)
    
    def prepare_training_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        objects = list(self.db["data_objects"].find())
        if len(objects) < 10:
            logging.warning("Insufficient data for training (need at least 10 objects)")
            return None, None
        features_list = []
        tier_labels = []
        location_labels = []
        for obj in objects:
            features = self._extract_features(obj["_id"])
            if features is not None:
                features_list.append(features)
                tier_labels.append(self.tier_mapping.get(obj["current_tier"], 1))
                location_labels.append(self.location_mapping.get(obj["current_location"], 0))
        if not features_list:
            return None, None
        X = pd.DataFrame(features_list)
        y_tier = pd.Series(tier_labels)
        y_location = pd.Series(location_labels)
        return X, (y_tier, y_location)
    
    def _extract_features(self, object_id: str) -> Dict:
        obj = self.db["data_objects"].find_one({"_id": object_id})
        if not obj:
            return None
        logs = list(self.db["access_logs"].find(
            {"data_object_id": object_id}
        ).sort("timestamp", -1).limit(100))
        if not logs:
            return {
                "size_gb": obj.get("size_bytes", 0) / (1024**3),
                "access_count": 0,
                "avg_latency": 100.0,
                "access_per_day": 0.0,
                "days_since_creation": (datetime.utcnow() - obj.get("created_at", datetime.utcnow())).days,
                "days_since_last_access": 999
            }
        recent_period = datetime.utcnow() - timedelta(days=7)
        recent_logs = [log for log in logs if log["timestamp"] >= recent_period]
        access_per_day = len(recent_logs) / 7.0
        avg_latency = sum(log.get("latency_ms", 100) for log in recent_logs) / max(len(recent_logs), 1)
        days_since_last = (datetime.utcnow() - obj.get("last_accessed", datetime.utcnow())).days
        days_since_creation = (datetime.utcnow() - obj.get("created_at", datetime.utcnow())).days
        return {
            "size_gb": obj.get("size_bytes", 0) / (1024**3),
            "access_count": obj.get("access_count", 0),
            "avg_latency": avg_latency,
            "access_per_day": access_per_day,
            "days_since_creation": days_since_creation,
            "days_since_last_access": days_since_last
        }
    
    def train_models(self):
        X, y = self.prepare_training_data()
        if X is None or len(X) < 10:
            logging.warning("Skipping model training due to insufficient data")
            return False
        y_tier, y_location = y
        X_scaled = self.scaler.fit_transform(X)
        self.tier_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.tier_model.fit(X_scaled, y_tier)
        self.location_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.location_model.fit(X_scaled, y_location)
        self._save_models()
        logging.info("ML models trained successfully")
        return True
    
    def _save_models(self):
        joblib.dump(self.tier_model, f"{self.model_path}/tier_model.pkl")
        joblib.dump(self.location_model, f"{self.model_path}/location_model.pkl")
        joblib.dump(self.scaler, f"{self.model_path}/scaler.pkl")
    
    def load_models(self):
        try:
            self.tier_model = joblib.load(f"{self.model_path}/tier_model.pkl")
            self.location_model = joblib.load(f"{self.model_path}/location_model.pkl")
            self.scaler = joblib.load(f"{self.model_path}/scaler.pkl")
            logging.info("ML models loaded successfully")
            return True
        except Exception as e:
            logging.warning(f"Could not load models: {str(e)}")
            return False
    
    def predict_optimal_placement(self, object_id: str) -> Tuple[str, str, float]:
        if not self.tier_model or not self.location_model:
            if not self.load_models():
                return "warm", "on-premise", 0.5
        features = self._extract_features(object_id)
        if not features:
            return "warm", "on-premise", 0.5
        X = pd.DataFrame([features])
        X_scaled = self.scaler.transform(X)
        tier_pred = self.tier_model.predict(X_scaled)[0]
        tier_proba = self.tier_model.predict_proba(X_scaled)[0]
        location_pred = self.location_model.predict(X_scaled)[0]
        location_proba = self.location_model.predict_proba(X_scaled)[0]
        predicted_tier = self.reverse_tier_mapping.get(tier_pred, "warm")
        predicted_location = self.reverse_location_mapping.get(location_pred, "on-premise")
        confidence = (max(tier_proba) + max(location_proba)) / 2.0
        return predicted_tier, predicted_location, confidence
    
    def batch_predict(self, limit: int = 100) -> Dict:
        objects = list(self.db["data_objects"].find().limit(limit))
        predictions = []
        for obj in objects:
            try:
                tier, location, confidence = self.predict_optimal_placement(obj["_id"])
                if tier != obj["current_tier"] or location != obj["current_location"]:
                    predictions.append({
                        "object_id": obj["_id"],
                        "name": obj["name"],
                        "current_tier": obj["current_tier"],
                        "current_location": obj["current_location"],
                        "predicted_tier": tier,
                        "predicted_location": location,
                        "confidence": round(confidence, 2)
                    })
            except Exception as e:
                logging.error(f"Prediction error for {obj['_id']}: {str(e)}")
        return {
            "predictions": sorted(predictions, key=lambda x: x["confidence"], reverse=True),
            "count": len(predictions)
        }
    
    def get_feature_importance(self) -> Dict:
        if not self.tier_model:
            return {}
        feature_names = ["size_gb", "access_count", "avg_latency", "access_per_day", "days_since_creation", "days_since_last_access"]
        tier_importance = dict(zip(feature_names, self.tier_model.feature_importances_))
        location_importance = dict(zip(feature_names, self.location_model.feature_importances_))
        return {
            "tier_prediction": {k: round(v, 3) for k, v in tier_importance.items()},
            "location_prediction": {k: round(v, 3) for k, v in location_importance.items()}
        }
