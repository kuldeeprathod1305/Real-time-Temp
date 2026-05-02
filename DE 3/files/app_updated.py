"""
Flask + ThingSpeak to Firebase integrated background worker.
Enhanced with EMAIL ALERT SYSTEM and TEMPERATURE PREDICTION for temperature monitoring.
"""

import time
import requests
import threading
import json
import numpy as np
from datetime import datetime, timezone, timedelta

# Indian Standard Time (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))
from flask import Flask, jsonify, render_template, request
from utils.alert_monitor import TemperatureAlertMonitor, get_alert_history
from utils.temperature_predictor import temperature_predictor

app = Flask(__name__)

# Custom JSON encoder to handle numpy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

app.json_encoder = NumpyEncoder

THINGSPEAK_CHANNEL_ID = "3134042"
THINGSPEAK_READ_API_KEY = ""
THINGSPEAK_BASE_URL = "https://api.thingspeak.com"

FIREBASE_DATABASE_URL = "https://realtime-database-71db5-default-rtdb.firebaseio.com"
DEVICE_ID   = "ESP32-001"
DEVICE_NAME = "ESP32 DHT22 Sensor"
LOCATION    = "Main Room"
POLL_INTERVAL_SECONDS = 60  # ⭐ Changed from 15 to 60 seconds (1 minute)

def fetch_latest_from_thingspeak() -> dict | None:
    url = f"{THINGSPEAK_BASE_URL}/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json"
    params = {"results": 1}
    if THINGSPEAK_READ_API_KEY:
        params["api_key"] = THINGSPEAK_READ_API_KEY

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        feeds = data.get("feeds", [])
        if not feeds:
            return None

        latest = feeds[-1]
        temp_raw = latest.get("field1")
        hum_raw  = latest.get("field2")

        if temp_raw is None or hum_raw is None:
            return None

        return {
            "temperature": float(temp_raw),
            "humidity":    float(hum_raw),
            "ts_timestamp": latest.get("created_at", ""),
        }
    except Exception as e:
        print(f"❌ ThingSpeak error: {e}")
        return None

def push_to_firebase(temperature: float, humidity: float, ts_timestamp: str) -> bool:
    now_utc = datetime.now(IST).isoformat()
    payload = {
        "deviceId":   DEVICE_ID,
        "deviceName": DEVICE_NAME,
        "location":   LOCATION,
        "temperature": round(temperature, 2),
        "humidity":    round(humidity, 2),
        "source":      "thingspeak-live",
        "status":      "active",
        "timestamp":   now_utc,
        "tsTimestamp": ts_timestamp,
    }

    url = f"{FIREBASE_DATABASE_URL}/temperatures.json"
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print(f"✅ Firebase push OK!")
        
        # Keep device status updated
        requests.patch(f"{FIREBASE_DATABASE_URL}/devices/{DEVICE_ID}.json", json={"status": "online"}, timeout=5)
        return True
    except Exception as e:
        print(f"❌ Firebase error: {e}")
        return False

def background_sync_task():
    print("=" * 60)
    print("  ThingSpeak -> Firebase Bridge (Background Thread Restored)")
    print("  ✨ EMAIL ALERT SYSTEM ENABLED")
    print("  🔮 TEMPERATURE PREDICTION ENABLED")
    print("=" * 60)
    time.sleep(2)
    last_ts_timestamp = None

    while True:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Fetching from ThingSpeak …")
        reading = fetch_latest_from_thingspeak()

        if reading:
            temp = reading["temperature"]
            hum  = reading["humidity"]
            ts   = reading["ts_timestamp"]

            if ts == last_ts_timestamp:
                print(f"  ⏳ No new data on ThingSpeak since last check ({ts}). Skipping push.")
            else:
                print(f"  🌡  Temperature : {temp} °C | 💧 Humidity    : {hum} %")
                print(f"  🕒 TS Time     : {ts} (NEW READING!)")

                if push_to_firebase(temp, hum, ts):
                    last_ts_timestamp = ts
                    
                    # Update global last_reading for API
                    global last_reading
                    last_reading = {
                        "temperature": temp,
                        "humidity": hum,
                        "ts_timestamp": ts,
                        "device_name": DEVICE_NAME
                    }
                    
                    # ✨ CHECK TEMPERATURE ALERT
                    print("\n🔍 Checking temperature alert conditions...")
                    alert_result = TemperatureAlertMonitor.check_temperature(
                        temperature=temp,
                        humidity=hum,
                        timestamp=ts,
                        device_name=DEVICE_NAME
                    )
                    
                    # Log alert result
                    print(f"   {alert_result['message']}")
                    if alert_result["alert_sent"]:
                        print(f"   ✅ EMAIL ALERT SENT: {alert_result['alert_reason']}")
        else:
            print("  ⚠️  Skipping Firebase push (no valid reading).")

        time.sleep(POLL_INTERVAL_SECONDS)

last_reading = {"temperature": 0, "humidity": 0, "ts_timestamp": "", "device_name": DEVICE_NAME}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/latest")
def get_latest():
    """API endpoint to get latest sensor reading"""
    return jsonify(last_reading)

@app.route("/api/history")
def get_history():
    """API endpoint to get historical data for the last 24 hours (approx 1500 readings at 1 per min)"""
    url = f"{FIREBASE_DATABASE_URL}/temperatures.json"
    params = {
        "orderBy": '"$key"',
        "limitToLast": 1440 # 24 hours * 60 mins
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data:
            return jsonify([])
        
        history_list = []
        for key, val in data.items():
            if isinstance(val, dict):
                history_list.append(val)
        
        # Sort by timestamp
        history_list.sort(key=lambda x: x.get("timestamp", ""))
        return jsonify(history_list)
    except Exception as e:
        print(f"❌ Error fetching history from Firebase: {e}")
        return jsonify([])

@app.route("/api/alert-status")
def get_alert_status():
    """API endpoint to get current alert system status"""
    return jsonify(TemperatureAlertMonitor.get_alert_status())

@app.route("/api/alert-history")
def get_alert_history_api():
    """API endpoint to get alert history"""
    return jsonify({"alerts": get_alert_history()})

@app.route("/api/reset-alerts", methods=["POST"])
def reset_alerts():
    """Admin endpoint to manually reset alert state (for testing)"""
    TemperatureAlertMonitor.reset_alerts()
    return jsonify({"status": "Alert state reset successfully"})

# ===============================================
#  🔮 PREDICTION ENDPOINTS
# ===============================================

@app.route("/api/predict")
def get_prediction():
    """
    API endpoint to get temperature prediction for a specific time in the future.
    Query parameters:
        minutes_ahead (int, default: 30) - How many minutes ahead to predict
    
    Returns:
        Prediction with confidence score, predicted temperature, and trend
    """
    try:
        minutes_ahead = request.args.get("minutes_ahead", 30, type=int)
        
        # Fetch historical data
        url = f"{FIREBASE_DATABASE_URL}/temperatures.json"
        params = {
            "orderBy": '"$key"',
            "limitToLast": 1440
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return jsonify({"error": "Insufficient historical data for prediction"}), 400
        
        history_list = []
        for key, val in data.items():
            if isinstance(val, dict):
                history_list.append(val)
        
        # Sort by timestamp
        history_list.sort(key=lambda x: x.get("timestamp", ""))
        
        # Get prediction
        prediction = temperature_predictor.predict(history_list, minutes_ahead)
        
        if not prediction:
            return jsonify({"error": "Could not generate prediction"}), 400
        
        return jsonify({
            "status": "success",
            "prediction": prediction,
            "data_points_used": len(history_list)
        })
    
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/predict/multiple")
def get_multiple_predictions():
    """
    API endpoint to get temperature predictions for multiple time intervals.
    Query parameters:
        intervals (str, default: "15,30,60,120") - Comma-separated minutes ahead
    
    Returns:
        Multiple predictions with trend direction
    """
    try:
        intervals_str = request.args.get("intervals", "15,30,60,120")
        intervals = [int(x.strip()) for x in intervals_str.split(",")]
        
        # Fetch historical data
        url = f"{FIREBASE_DATABASE_URL}/temperatures.json"
        params = {
            "orderBy": '"$key"',
            "limitToLast": 1440
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return jsonify({"error": "Insufficient historical data"}), 400
        
        history_list = []
        for key, val in data.items():
            if isinstance(val, dict):
                history_list.append(val)
        
        history_list.sort(key=lambda x: x.get("timestamp", ""))
        
        # Get multiple predictions
        predictions = temperature_predictor.predict_multiple(history_list, intervals)
        
        if not predictions:
            return jsonify({"error": "Could not generate predictions"}), 400
        
        return jsonify({
            "status": "success",
            "predictions_data": predictions,
            "data_points_used": len(history_list)
        })
    
    except Exception as e:
        print(f"❌ Multiple predictions error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/predict/24h-forecast")
def get_forecast_24h():
    """
    API endpoint to get hourly temperature forecast for next 24 hours.
    
    Returns:
        Hourly predictions, summary statistics, and trend
    """
    try:
        # Fetch historical data
        url = f"{FIREBASE_DATABASE_URL}/temperatures.json"
        params = {
            "orderBy": '"$key"',
            "limitToLast": 1440
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return jsonify({"error": "Insufficient historical data"}), 400
        
        history_list = []
        for key, val in data.items():
            if isinstance(val, dict):
                history_list.append(val)
        
        history_list.sort(key=lambda x: x.get("timestamp", ""))
        
        # Get 24-hour forecast
        forecast = temperature_predictor.predict_trend_24h(history_list)
        
        if not forecast:
            return jsonify({"error": "Could not generate forecast"}), 400
        
        return jsonify({
            "status": "success",
            "forecast_24h": forecast,
            "data_points_used": len(history_list)
        })
    
    except Exception as e:
        print(f"❌ 24h forecast error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/predict/moving-average")
def get_moving_average():
    """
    API endpoint to get temperature moving average (smoothed data).
    Query parameters:
        window (int, default: 5) - Window size for moving average
    
    Returns:
        Temperature data smoothed with moving average
    """
    try:
        window = request.args.get("window", 5, type=int)
        
        # Fetch historical data
        url = f"{FIREBASE_DATABASE_URL}/temperatures.json"
        params = {
            "orderBy": '"$key"',
            "limitToLast": 1440
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return jsonify({"error": "No data available"}), 400
        
        history_list = []
        for key, val in data.items():
            if isinstance(val, dict):
                history_list.append(val)
        
        history_list.sort(key=lambda x: x.get("timestamp", ""))
        
        # Get moving average
        ma_data = temperature_predictor.get_moving_average(history_list, window)
        
        return jsonify({
            "status": "success",
            "moving_average": ma_data,
            "window_size": window,
            "data_points": len(ma_data)
        })
    
    except Exception as e:
        print(f"❌ Moving average error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/predict/anomalies")
def get_anomaly_detection():
    """
    API endpoint to detect temperature anomalies.
    Query parameters:
        threshold_std (float, default: 2.0) - Standard deviations for anomaly threshold
    
    Returns:
        Detected anomalies with deviation information
    """
    try:
        threshold_std = request.args.get("threshold_std", 2.0, type=float)
        
        # Fetch historical data
        url = f"{FIREBASE_DATABASE_URL}/temperatures.json"
        params = {
            "orderBy": '"$key"',
            "limitToLast": 1440
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return jsonify({"error": "No data available"}), 400
        
        history_list = []
        for key, val in data.items():
            if isinstance(val, dict):
                history_list.append(val)
        
        history_list.sort(key=lambda x: x.get("timestamp", ""))
        
        # Detect anomalies
        anomalies = temperature_predictor.analyze_anomalies(history_list, threshold_std)
        
        if not anomalies:
            return jsonify({"error": "Could not analyze anomalies"}), 400
        
        # Transform response to match test expectations
        anomaly_threshold_celsius = anomalies['std'] * threshold_std
        
        # Extract anomalies with additional fields
        anomalies_list = []
        for anom in anomalies['anomalies']:
            anom_record = {
                'timestamp': anom.get('timestamp', ''),
                'temperature': anom.get('temperature', 0),
                'z_score': anom.get('z_score', 0),
                'std_devs_away': anom.get('z_score', 0),
                'deviation': abs(float(anom.get('temperature', 0)) - float(anomalies['mean']))
            }
            anomalies_list.append(anom_record)
        
        return jsonify({
            "status": "success",
            "anomaly_analysis": {
                "mean_temperature": anomalies['mean'],
                "std_deviation": anomalies['std'],
                "anomaly_threshold": anomaly_threshold_celsius,
                "anomalies_detected": anomalies['anomaly_count'],
                "anomalies": anomalies_list,
                "threshold_std": threshold_std
            }
        })
    
    except Exception as e:
        print(f"❌ Anomaly detection error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    sync_thread = threading.Thread(target=background_sync_task, daemon=True)
    sync_thread.start()
    app.run(host="0.0.0.0", port=5000, debug=False)
