"""
Temperature Prediction Module
Uses linear regression and moving averages to predict future temperatures.
Provides short-term (next 30-60 min) and medium-term (next 6-24 hours) predictions.
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sklearn.linear_model import LinearRegression
import json


class TemperaturePredictor:
    """
    Predicts future temperatures based on historical data.
    Uses multiple algorithms for robust predictions.
    """

    def __init__(self, min_data_points: int = 10):
        """
        Initialize predictor.
        
        Args:
            min_data_points: Minimum historical points needed for prediction
        """
        self.min_data_points = min_data_points
        self.model = None
        self.last_update = None

    def prepare_data(self, history: List[Dict]) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Prepares historical data for prediction.
        Converts timestamps to minutes since epoch and extracts temperatures.
        
        Args:
            history: List of temperature records with 'timestamp' and 'temperature' keys
            
        Returns:
            Tuple of (X, y) arrays or (None, None) if insufficient data
        """
        if not history or len(history) < self.min_data_points:
            print(f"⚠️  Insufficient data for prediction. Need {self.min_data_points}, got {len(history)}")
            return None, None

        try:
            # Extract timestamps and temperatures
            timestamps = []
            temperatures = []
            
            for record in history:
                if "timestamp" in record and "temperature" in record:
                    try:
                        # Parse ISO format timestamp
                        ts = datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00"))
                        temp = float(record["temperature"])
                        
                        timestamps.append(ts)
                        temperatures.append(temp)
                    except (ValueError, TypeError):
                        continue
            
            if len(temperatures) < self.min_data_points:
                print(f"⚠️  Not enough valid data points: {len(temperatures)}")
                return None, None
            
            # Sort by timestamp
            sorted_data = sorted(zip(timestamps, temperatures), key=lambda x: x[0])
            timestamps, temperatures = zip(*sorted_data)
            
            # Convert timestamps to minutes since first reading
            start_time = timestamps[0]
            X = np.array([(ts - start_time).total_seconds() / 60 for ts in timestamps]).reshape(-1, 1)
            y = np.array(temperatures)
            
            self.last_update = datetime.now()
            return X, y
            
        except Exception as e:
            print(f"❌ Error preparing data: {e}")
            return None, None

    def train(self, history: List[Dict]) -> bool:
        """
        Trains the prediction model on historical data.
        
        Args:
            history: List of temperature records
            
        Returns:
            True if training successful, False otherwise
        """
        X, y = self.prepare_data(history)
        
        if X is None or y is None:
            return False
        
        try:
            self.model = LinearRegression()
            self.model.fit(X, y)
            print(f"✅ Model trained on {len(y)} data points")
            return True
        except Exception as e:
            print(f"❌ Model training error: {e}")
            return False

    def predict(self, history: List[Dict], minutes_ahead: int = 30) -> Optional[Dict]:
        """
        Predicts temperature for a given time in the future.
        
        Args:
            history: Historical temperature data
            minutes_ahead: How many minutes ahead to predict (default: 30)
            
        Returns:
            Dictionary with prediction details or None if failed
        """
        if not self.train(history):
            return None
        
        try:
            # Get last timestamp
            timestamps = []
            for record in history:
                if "timestamp" in record:
                    try:
                        ts = datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00"))
                        timestamps.append(ts)
                    except ValueError:
                        continue
            
            if not timestamps:
                return None
            
            last_timestamp = max(timestamps)
            start_time = min(timestamps)
            
            # Calculate minutes from start to last reading
            minutes_elapsed = (last_timestamp - start_time).total_seconds() / 60
            
            # Predict at future time
            future_minutes = minutes_elapsed + minutes_ahead
            future_temp = float(self.model.predict([[future_minutes]])[0])
            
            # Calculate prediction confidence (R² score)
            X, y = self.prepare_data(history)
            confidence = float(self.model.score(X, y)) * 100
            confidence = max(0, min(100, confidence))  # Clamp 0-100
            
            future_time = last_timestamp + timedelta(minutes=minutes_ahead)
            
            return {
                "predicted_temperature": round(future_temp, 2),
                "prediction_time": future_time.isoformat(),
                "minutes_ahead": minutes_ahead,
                "confidence_percentage": round(confidence, 2),
                "model_slope": round(float(self.model.coef_[0]), 4),  # Rate of change per minute
                "last_recorded_temp": float(y[-1]),
                "last_recorded_time": last_timestamp.isoformat()
            }
        
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            return None

    def predict_multiple(self, history: List[Dict], 
                        intervals: List[int] = None) -> Optional[Dict]:
        """
        Generates predictions for multiple future time points.
        
        Args:
            history: Historical temperature data
            intervals: List of minute intervals to predict (default: [15, 30, 60, 120])
            
        Returns:
            Dictionary with multiple predictions
        """
        if intervals is None:
            intervals = [15, 30, 60, 120]
        
        predictions = []
        
        for minutes in intervals:
            pred = self.predict(history, minutes)
            if pred:
                predictions.append(pred)
        
        if not predictions:
            return None
        
        return {
            "predictions": predictions,
            "prediction_time_generated": datetime.now().isoformat(),
            "data_points_used": len(history),
            "trend_direction": "↗️ Increasing" if predictions[-1]["model_slope"] > 0 else "↘️ Decreasing"
        }

    def predict_trend_24h(self, history: List[Dict]) -> Optional[Dict]:
        """
        Generates hourly predictions for the next 24 hours.
        
        Args:
            history: Historical temperature data
            
        Returns:
            Dictionary with hourly predictions for 24 hours
        """
        hourly_predictions = []
        
        for hour in range(1, 25):
            minutes = hour * 60
            pred = self.predict(history, minutes)
            if pred:
                hourly_predictions.append({
                    "hour": hour,
                    "predicted_temperature": pred["predicted_temperature"],
                    "confidence_percentage": pred["confidence_percentage"],
                    "time": pred["prediction_time"]
                })
        
        if not hourly_predictions:
            return None
        
        # Calculate statistics
        temps = [p["predicted_temperature"] for p in hourly_predictions]
        
        return {
            "hourly_forecast": hourly_predictions,
            "summary": {
                "predicted_max": max(temps),
                "predicted_min": min(temps),
                "predicted_avg": round(sum(temps) / len(temps), 2),
                "max_hour": hourly_predictions[temps.index(max(temps))]["hour"],
                "min_hour": hourly_predictions[temps.index(min(temps))]["hour"]
            },
            "trend_24h": "↗️ Warming trend" if temps[-1] > temps[0] else "↘️ Cooling trend"
        }

    def get_moving_average(self, history: List[Dict], window: int = 5) -> List[Dict]:
        """
        Calculates moving average to smooth out noise in data.
        
        Args:
            history: Historical temperature data
            window: Window size for moving average (default: 5 readings)
            
        Returns:
            List of records with moving average temperature
        """
        if not history or len(history) < window:
            return []
        
        try:
            # Sort by timestamp
            sorted_history = sorted(
                history,
                key=lambda x: x.get("timestamp", "")
            )
            
            moving_avg_data = []
            
            for i in range(len(sorted_history)):
                start_idx = max(0, i - window + 1)
                window_data = sorted_history[start_idx:i+1]
                
                temps = [r["temperature"] for r in window_data if "temperature" in r]
                if temps:
                    avg_temp = sum(temps) / len(temps)
                    
                    moving_avg_data.append({
                        "timestamp": sorted_history[i].get("timestamp"),
                        "temperature": round(avg_temp, 2),
                        "window_size": len(temps)
                    })
            
            return moving_avg_data
        
        except Exception as e:
            print(f"❌ Moving average error: {e}")
            return []

    def analyze_anomalies(self, history: List[Dict], 
                         threshold_std: float = 2.0) -> Optional[Dict]:
        """
        Detects temperature anomalies based on standard deviation.
        
        Args:
            history: Historical temperature data
            threshold_std: Standard deviations from mean to flag as anomaly
            
        Returns:
            Dictionary with anomaly analysis
        """
        if not history or len(history) < 5:
            return None
        
        try:
            temps = [r["temperature"] for r in history if "temperature" in r]
            
            if len(temps) < 5:
                return None
            
            mean_temp = np.mean(temps)
            std_temp = np.std(temps)
            
            anomalies = []
            for i, record in enumerate(history):
                temp = record.get("temperature")
                if temp and abs(temp - mean_temp) > (threshold_std * std_temp):
                    anomalies.append({
                        "index": i,
                        "temperature": temp,
                        "timestamp": record.get("timestamp"),
                        "deviation": round(abs(temp - mean_temp), 2),
                        "std_devs_away": round(abs(temp - mean_temp) / std_temp, 2)
                    })
            
            return {
                "mean_temperature": round(mean_temp, 2),
                "std_deviation": round(std_temp, 2),
                "anomaly_threshold": round(threshold_std * std_temp, 2),
                "anomalies_detected": len(anomalies),
                "anomalies": anomalies[:10]  # Return top 10
            }
        
        except Exception as e:
            print(f"❌ Anomaly analysis error: {e}")
            return None


# Global predictor instance
temperature_predictor = TemperaturePredictor()
