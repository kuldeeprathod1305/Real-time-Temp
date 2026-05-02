"""
Full system health check for the Real-Time Temperature Monitoring System
"""
import sys
import os
import pathlib

print("=" * 60)
print("  SYSTEM HEALTH CHECK")
print("=" * 60)

# ── 1. Python version ──────────────────────────────────────────
print(f"\n[1] Python : {sys.version.split()[0]}")

# ── 2. Package check ───────────────────────────────────────────
print("\n[2] Required packages:")
pkgs = {
    "requests": "requests",
    "flask": "flask",
    "dotenv": "dotenv",
    "sklearn": "sklearn",
    "pandas": "pandas",
    "numpy": "numpy",
}
all_ok = True
for label, pkg in pkgs.items():
    try:
        mod = __import__(pkg)
        ver = getattr(mod, "__version__", "installed")
        print(f"    [OK]      {label} == {ver}")
    except ImportError as e:
        print(f"    [MISSING] {label}: {e}")
        all_ok = False

# ── 3. .env / config ───────────────────────────────────────────
print("\n[3] .env config:")
from dotenv import load_dotenv
load_dotenv()
keys = ["EMAIL_USER", "EMAIL_PASS", "RECIPIENT_EMAIL", "TEMP_THRESHOLD",
        "ALERT_COOLDOWN", "FIREBASE_DATABASE_URL", "DEVICE_ID", "DEVICE_NAME"]
for k in keys:
    v = os.getenv(k, "NOT SET")
    masked = v[:4] + "****" if k == "EMAIL_PASS" and v != "NOT SET" else v
    print(f"    {k:22s} = {masked}")

# ── 4. Model files ─────────────────────────────────────────────
print("\n[4] ML model files:")
for p in ["ml/model.pkl", "ml/scaler.pkl", "ml/preprocess.py", "ml/train_model.py"]:
    fp = pathlib.Path(p)
    if fp.exists():
        size = fp.stat().st_size
        print(f"    [OK] {p}  ({size // 1024} KB)")
    else:
        print(f"    [MISSING] {p}")

# ── 5. Connectivity tests ──────────────────────────────────────
print("\n[5] Connectivity:")
import requests as req

# ThingSpeak
try:
    url = "https://api.thingspeak.com/channels/3134042/feeds.json?results=1"
    r = req.get(url, timeout=10)
    data = r.json()
    feeds = data.get("feeds", [])
    if feeds:
        f = feeds[-1]
        print(f"    [OK] ThingSpeak  -> Temp={f.get('field1')} C  Hum={f.get('field2')} %  @{f.get('created_at')}")
    else:
        print("    [WARN] ThingSpeak -> Connected but no feeds returned")
except Exception as e:
    print(f"    [FAIL] ThingSpeak -> {e}")

# Firebase
FIREBASE_URL = os.getenv("FIREBASE_DATABASE_URL", "https://realtime-database-71db5-default-rtdb.firebaseio.com")
try:
    r = req.get(f"{FIREBASE_URL}/temperatures.json?orderBy=%22%24key%22&limitToLast=1", timeout=10)
    r.raise_for_status()
    data = r.json()
    if data:
        last_key = list(data.keys())[-1]
        last_val = data[last_key]
        print(f"    [OK] Firebase    -> Last entry Temp={last_val.get('temperature')} C  Hum={last_val.get('humidity')} %  @{last_val.get('timestamp','?')[:19]}")
    else:
        print("    [WARN] Firebase -> Connected but /temperatures is empty")
except Exception as e:
    print(f"    [FAIL] Firebase  -> {e}")

# ── 6. Import app modules ──────────────────────────────────────
print("\n[6] App module imports:")
try:
    from utils.alert_monitor import TemperatureAlertMonitor, get_alert_history
    print("    [OK] utils.alert_monitor")
except Exception as e:
    print(f"    [FAIL] utils.alert_monitor: {e}")

try:
    from utils.predictor import predict_next_day, is_model_ready
    ready = is_model_ready()
    print(f"    [OK] utils.predictor  (model_ready={ready})")
except Exception as e:
    print(f"    [FAIL] utils.predictor: {e}")

print("\n" + "=" * 60)
print("  HEALTH CHECK COMPLETE")
print("=" * 60)
