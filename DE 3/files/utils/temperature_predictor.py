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

    def __init__(self, min_data_points: int = 5):
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
            print(f"⚠️  Insufficient data for prediction. Need {self.min_data_points}, got {len(history) if history else 0}")
            return None, None

        try:
            # Extract timestamps and temperatures
            timestamps = []
            temperatures = []
            
            for i, record in enumerate(history):
                temperature = record.get('temperature')
                
                if temperature is not None:
                    timestamps.append(i)  # Use index as time representation
                    temperatures.append(float(temperature))
            
            if len(temperatures) < self.min_data_points:
                return None, None
            
            # Convert to numpy arrays
            X = np.array(timestamps).reshape(-1, 1)
            y = np.array(temperatures)
            
            return X, y
        
        except Exception as e:
            print(f"❌ Error preparing data: {e}")
            return None, None

    def train(self, history: List[Dict]) -> bool:
        """
        Train linear regression model on historical data.
        
        Args:
            history: List of temperature records
            
        Returns:
            True if successful, False otherwise
        """
        X, y = self.prepare_data(history)
        
        if X is None:
            return False
        
        try:
            self.model = LinearRegression()
            self.model.fit(X, y)
            self.last_update = datetime.now()
            return True
        
        except Exception as e:
            print(f"❌ Error training model: {e}")
            return False

    def predict(self, history: List[Dict], minutes_ahead: int) -> Optional[Dict]:
        """
        Predict temperature at a specific time in the future.
        
        Args:
            history: List of historical temperature records
            minutes_ahead: Number of minutes in the future to predict
            
        Returns:
            Dictionary with prediction and confidence, or None if prediction not available
        """
        if not history:
            return None
        
        try:
            # Train model on history
            if not self.train(history):
                return None
            
            # Predict based on trend
            last_temp = float(history[-1].get('temperature', 0))
            data_points = len(history)
            
            # Create prediction point
            future_idx = data_points + max(1, minutes_ahead // 60)
            future_X = np.array([[future_idx]])
            
            predicted_temp = self.model.predict(future_X)[0]
            
            # Calculate confidence based on how far we're predicting
            # Closer predictions have higher confidence
            confidence = max(0, min(100, 100 - (minutes_ahead / 1440) * 50))
            
            # Calculate trend and slope
            trend = "warming" if predicted_temp > last_temp else "cooling" if predicted_temp < last_temp else "stable"
            temp_change = float(predicted_temp - last_temp)
            model_slope = temp_change / max(1, minutes_ahead) if minutes_ahead > 0 else 0
            
            return {
                "predicted_temperature": round(float(predicted_temp), 2),
                "current_temperature": round(last_temp, 2),
                "last_recorded_temp": round(last_temp, 2),
                "minutes_ahead": minutes_ahead,
                "confidence": round(confidence, 1),
                "confidence_percentage": round(confidence, 1),
                "trend": trend,
                "trend_direction": trend,
                "temperature_change": round(temp_change, 2),
                "model_slope": round(model_slope, 6)
            }
        
        except Exception as e:
            print(f"❌ Error making prediction: {e}")
            return None

    def predict_multiple(self, history: List[Dict], intervals: List[int]) -> Optional[Dict]:
        """
        Generate predictions for multiple time intervals.
        
        Args:
            history: List of temperature records
            intervals: List of minutes ahead to predict
            
        Returns:
            Dictionary with multiple predictions or None
        """
        try:
            predictions = []
            
            for minutes in intervals:
                prediction = self.predict(history, minutes)
                if prediction:
                    predictions.append(prediction)
            
            if not predictions:
                return None
            
            # Determine overall trend direction
            trend_direction = "warming" if predictions[-1]["predicted_temperature"] > predictions[0]["predicted_temperature"] else "cooling" if predictions[-1]["predicted_temperature"] < predictions[0]["predicted_temperature"] else "stable"
            
            return {
                "predictions": predictions,
                "predictions_data": {
                    "predictions": predictions,
                    "trend_direction": trend_direction,
                    "count": len(predictions)
                },
                "count": len(predictions),
                "trend_direction": trend_direction
            }
        
        except Exception as e:
            print(f"❌ Error in predict_multiple: {e}")
            return None

    def predict_trend_24h(self, history: List[Dict]) -> Optional[Dict]:
        """
        Generate 24-hour forecast with hourly predictions.
        
        Args:
            history: List of temperature records
            
        Returns:
            Dictionary with hourly predictions for next 24 hours or None
        """
        try:
            if not history:
                return None
            
            # Train model
            if not self.train(history):
                return None
            
            last_temp = float(history[-1].get('temperature', 0))
            forecast = []
            temperatures_predicted = [last_temp]
            
            for hour in range(1, 25):
                minutes_ahead = hour * 60
                prediction = self.predict(history, minutes_ahead)
                
                if prediction:
                    prediction['hour'] = hour
                    # Ensure confidence_percentage is set
                    if 'confidence_percentage' not in prediction:
                        prediction['confidence_percentage'] = prediction.get('confidence', 0)
                    forecast.append(prediction)
                    temperatures_predicted.append(prediction['predicted_temperature'])
            
            # Calculate summary stats
            if temperatures_predicted:
                temps_array = np.array(temperatures_predicted)
                max_idx = np.argmax(temps_array)
                min_idx = np.argmin(temps_array)
                
                summary = {
                    "predicted_min": round(float(np.min(temps_array)), 2),
                    "predicted_max": round(float(np.max(temps_array)), 2),
                    "predicted_avg": round(float(np.mean(temps_array)), 2),
                    "min_hour": max(0, max_idx - 1),  # -1 because index 0 is current
                    "max_hour": max(0, min_idx - 1),  # -1 because index 0 is current
                    "trend": "warming" if temperatures_predicted[-1] > temperatures_predicted[0] else "cooling" if temperatures_predicted[-1] < temperatures_predicted[0] else "stable"
                }
            else:
                summary = None
            
            trend_24h = "warming" if temperatures_predicted[-1] > temperatures_predicted[0] else "cooling" if temperatures_predicted[-1] < temperatures_predicted[0] else "stable"
            
            return {
                "forecast": forecast,
                "forecast_24h": {
                    "hourly_forecast": forecast,
                    "summary": summary,
                    "trend_24h": trend_24h,
                    "hours_count": len(forecast)
                },
                "hourly_forecast": forecast,  # Add this for direct access
                "summary": summary,
                "hours_count": len(forecast),
                "trend_24h": trend_24h
            }
        
        except Exception as e:
            print(f"❌ Error in predict_trend_24h: {e}")
            return None

    def get_moving_average(self, history: List[Dict], window_size: int = 5) -> Optional[List[Dict]]:
        """
        Calculate moving average to smooth temperature data.
        
        Args:
            history: List of temperature records
            window_size: Number of points for moving average
            
        Returns:
            List of smoothed records or None if error
        """
        if not history or len(history) < 1:
            return None
        
        try:
            smoothed = []
            temperatures = [r.get('temperature', 0) for r in history]
            
            for i in range(len(temperatures)):
                start_idx = max(0, i - window_size + 1)
                window = temperatures[start_idx:i + 1]
                avg = sum(window) / len(window) if window else 0
                
                record = history[i].copy() if isinstance(history[i], dict) else {"temperature": temperatures[i]}
                record['smoothed_temperature'] = round(avg, 2)
                record['window_size'] = len(window)
                smoothed.append(record)
            
            return smoothed
        
        except Exception as e:
            print(f"❌ Error calculating moving average: {e}")
            return None

    def analyze_anomalies(self, history: List[Dict], threshold: float = 2.0) -> Optional[Dict]:
        """
        Detect temperature anomalies using standard deviation.
        
        Args:
            history: List of temperature records
            threshold: Number of standard deviations for anomaly threshold
            
        Returns:
            Dictionary with anomaly analysis or None if error
        """
        if not history or len(history) < 3:
            return None
        
        try:
            temperatures = np.array([r.get('temperature', 0) for r in history])
            
            mean = np.mean(temperatures)
            std = np.std(temperatures)
            
            anomalies = []
            normal_count = 0
            
            for i, record in enumerate(history):
                temp = float(record.get('temperature', 0))
                z_score = abs((temp - mean) / std) if std > 0 else 0
                # Convert to native Python bool to avoid JSON serialization issues
                is_anomaly = bool(float(z_score) > float(threshold))
                
                record_copy = record.copy() if isinstance(record, dict) else {"temperature": temp}
                record_copy['is_anomaly'] = is_anomaly
                record_copy['z_score'] = round(float(z_score), 2)
                anomalies.append(record_copy)
                
                if not is_anomaly:
                    normal_count += 1
            
            anomaly_records = [a for a in anomalies if a['is_anomaly']]
            
            return {
                "anomalies": anomaly_records,
                "anomaly_count": int(len(anomaly_records)),
                "normal_count": int(normal_count),
                "threshold": float(threshold),
                "mean": round(float(mean), 2),
                "std": round(float(std), 2),
                "all_records": anomalies
            }
        
        except Exception as e:
            print(f"❌ Error detecting anomalies: {e}")
            return None


# Global instance for Flask routes
temperature_predictor = TemperaturePredictor()
