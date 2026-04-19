"""
Flask + ThingSpeak to Firebase integrated background worker.
Enhanced with EMAIL ALERT SYSTEM for temperature monitoring.
"""

import time
import requests
import threading
import json
from datetime import datetime, timezone, timedelta

# Indian Standard Time (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))
from flask import Flask, jsonify, render_template
from utils.alert_monitor import TemperatureAlertMonitor, get_alert_history

app = Flask(__name__)

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

if __name__ == "__main__":
    sync_thread = threading.Thread(target=background_sync_task, daemon=True)
    sync_thread.start()
    app.run(host="0.0.0.0", port=5000, debug=False)
