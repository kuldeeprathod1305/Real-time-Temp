"""
Flask + ThingSpeak to Firebase integrated background worker.
Enhanced with EMAIL ALERT SYSTEM and ML TEMPERATURE PREDICTION.
"""

import time
import requests
import threading
import json
from datetime import datetime, timezone, timedelta

# Indian Standard Time (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))
from flask import Flask, jsonify, render_template, make_response
from utils.alert_monitor import TemperatureAlertMonitor, get_alert_history
from utils.predictor import predict_next_day, is_model_ready

app = Flask(__name__)

THINGSPEAK_CHANNEL_ID = "3134042"
THINGSPEAK_READ_API_KEY = ""
THINGSPEAK_BASE_URL = "https://api.thingspeak.com"

FIREBASE_DATABASE_URL = "https://realtime-database-71db5-default-rtdb.firebaseio.com"
DEVICE_ID   = "ESP32-001"
DEVICE_NAME = "ESP32 DHT22 Sensor"
LOCATION    = "Main Room"
POLL_INTERVAL_SECONDS = 60  # Changed from 15 to 60 seconds (1 minute)

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
        print(f"[ERROR] ThingSpeak error: {e}")
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
        print(f"[OK] Firebase push OK!")
        
        # Keep device status updated
        requests.patch(f"{FIREBASE_DATABASE_URL}/devices/{DEVICE_ID}.json", json={"status": "online"}, timeout=5)
        return True
    except Exception as e:
        print(f"[ERROR] Firebase error: {e}")
        return False

def background_sync_task():
    print("=" * 60)
    print("  ThingSpeak -> Firebase Bridge (Background Thread Restored)")
    print("  [*] EMAIL ALERT SYSTEM ENABLED")
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
                print(f"  [WAIT] No new data on ThingSpeak since last check ({ts}). Skipping push.")
            else:
                print(f"  [TEMP] Temperature : {temp} C | [HUM] Humidity : {hum} %")
                print(f"  [TIME] TS Time     : {ts} (NEW READING!)")

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
                    
                    # CHECK TEMPERATURE ALERT
                    print("\n[CHECK] Checking temperature alert conditions...")
                    alert_result = TemperatureAlertMonitor.check_temperature(
                        temperature=temp,
                        humidity=hum,
                        timestamp=ts,
                        device_name=DEVICE_NAME
                    )
                    
                    # Log alert result
                    print(f"   {alert_result['message']}")
                    if alert_result["alert_sent"]:
                        print(f"   [ALERT SENT] EMAIL ALERT SENT: {alert_result['alert_reason']}")
        else:
            print("  [WARN] Skipping Firebase push (no valid reading).")

        time.sleep(POLL_INTERVAL_SECONDS)

last_reading = {"temperature": 0, "humidity": 0, "ts_timestamp": "", "device_name": DEVICE_NAME}

# ── Prediction cache — updated every 10 minutes ────────────────────────────
PREDICT_INTERVAL = 600   # seconds
prediction_cache = {
    "predicted_temp": None,
    "alert": False,
    "alert_message": "",
    "threshold": 35.0,
    "confidence": "N/A",
    "model_loaded": False,
    "timestamp": None,
    "error": "Model not yet evaluated. Waiting for first prediction cycle."
}

def background_prediction_task():
    """Refresh prediction cache every PREDICT_INTERVAL seconds."""
    global prediction_cache
    print("[Predictor] Background prediction thread started.")
    time.sleep(10)  # Let the main bridge thread warm up first

    while True:
        try:
            # Fetch last 24-hour history from Firebase
            url    = f"{FIREBASE_DATABASE_URL}/temperatures.json"
            params = {"orderBy": '"$key"', "limitToLast": 1440}
            resp   = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            raw = resp.json() or {}

            history = sorted(
                [v for v in raw.values() if isinstance(v, dict)],
                key=lambda x: x.get("timestamp", "")
            )

            result = predict_next_day(history)
            prediction_cache = result

            status_icon = "[ALERT]" if result.get("alert") else "[OK]"
            temp_str    = f"{result.get('predicted_temp', 'N/A')} C"
            print(f"[Predictor] {status_icon} Next-day prediction: {temp_str}")

        except Exception as exc:
            print(f"[Predictor] [ERROR] Error refreshing prediction: {exc}")

        time.sleep(PREDICT_INTERVAL)

@app.route("/")
def index():
    resp = make_response(render_template("index.html"))
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

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
        print(f"[ERROR] Error fetching history from Firebase: {e}")
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

@app.route("/predict")
def get_prediction():
    """API endpoint returning next-day temperature prediction."""
    # If cache has a fresh prediction, serve it immediately
    if prediction_cache.get("timestamp"):
        return jsonify(prediction_cache)

    # Otherwise run a synchronous prediction with current last_reading as fallback
    readings = [last_reading] if last_reading.get("temperature") else []
    result   = predict_next_day(readings)
    return jsonify(result)


@app.route("/api/model-status")
def get_model_status():
    """API endpoint to check if the ML model is loaded and ready."""
    return jsonify({
        "model_ready": is_model_ready(),
        "last_prediction": prediction_cache
    })


if __name__ == "__main__":
    # Start ThingSpeak → Firebase bridge thread
    sync_thread = threading.Thread(target=background_sync_task, daemon=True)
    sync_thread.start()

    # Start ML prediction refresh thread
    predict_thread = threading.Thread(target=background_prediction_task, daemon=True)
    predict_thread.start()

    app.run(host="0.0.0.0", port=5000, debug=False)
