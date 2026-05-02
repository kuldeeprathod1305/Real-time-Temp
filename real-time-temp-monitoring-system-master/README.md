<div align="center">

<h1>🌡️ Real-Time IoT Temperature Monitoring System</h1>

<p>
  <strong>Production-grade IoT pipeline · ESP32 + DHT22 · Firebase · Flask · Random Forest ML</strong>
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Flask-Backend-black?style=for-the-badge&logo=flask"/>
  <img src="https://img.shields.io/badge/Firebase-Realtime%20DB-orange?style=for-the-badge&logo=firebase"/>
  <img src="https://img.shields.io/badge/ESP32-Firmware-red?style=for-the-badge&logo=espressif"/>
  <img src="https://img.shields.io/badge/ML-Random%20Forest-green?style=for-the-badge&logo=scikit-learn"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge"/>
</p>

<p>
  <a href="#-demo">View Demo</a> ·
  <a href="#-quick-start">Quick Start</a> ·
  <a href="#-architecture">Architecture</a> ·
  <a href="#-api-reference">API Docs</a> ·
  <a href="#-ml-pipeline">ML Pipeline</a>
</p>

</div>

---

## 📌 Overview

A **full-stack, real-time IoT monitoring system** that streams temperature data from an ESP32 sensor all the way to a live web dashboard — with built-in ML-powered temperature prediction, email alerting, and Firebase cloud storage.

> Built as a complete Data Engineering project demonstrating end-to-end IoT → Cloud → ML → Dashboard pipeline.

### Why This Project?

| Problem | Our Solution |
|---|---|
| Raw sensor data is hard to act on | Real-time dashboard with live gauge + trend charts |
| No early warning system | Email alerts when temperature exceeds threshold |
| No predictive capability | Random Forest ML model predicts next temperature |
| Data is siloed in ThingSpeak | Firebase bridge persists history for analytics |

---

## ✨ Features

- 📡 **Real-Time Streaming** — ESP32 + DHT22 pushes readings every 60 seconds via Wi-Fi
- ☁️ **ThingSpeak → Firebase Bridge** — background Flask thread syncs data to cloud storage
- 🌡️ **Animated Live Gauge** — 270° SVG arc with smooth transitions, color-coded by temperature
- 📊 **Trend Charts** — Chart.js rolling 1-hour window split into 15-minute segments
- 🤖 **ML Predictions** — Random Forest Regressor predicts next-step temperature (R² = 0.955)
- 📧 **Smart Email Alerts** — Gmail SMTP alerts with 3-retry logic and cooldown spam protection
- 🔄 **Auto-Refresh** — Dashboard polls for new readings every 60 seconds
- 📜 **Historical Analytics** — Min/Max stats for 1h / 6h / 24h windows from Firebase

---

## 🖼️ Demo

| Dashboard | Live Gauge | ML Prediction Panel |
|---|---|---|
| Dark theme with live data | 270° animated SVG ring | Next-step temperature forecast |

> Open `http://127.0.0.1:5000` after running `python app.py`

---

## 🏗️ Architecture

```
┌─────────────────┐
│  ESP32 + DHT22  │  (sensor reads every 60s)
└────────┬────────┘
         │ Wi-Fi / HTTP
         ▼
┌─────────────────┐
│   ThingSpeak    │  (IoT cloud channel, field1=Temp, field2=Humidity)
└────────┬────────┘
         │ REST API poll (every 60s)
         ▼
┌──────────────────────────────────────────┐
│          Flask Backend (app.py)          │
│                                          │
│  ┌────────────────┐  ┌────────────────┐  │
│  │ Background     │  │  Web Server    │  │
│  │ Sync Thread    │  │  + REST API    │  │
│  └───────┬────────┘  └───────┬────────┘  │
└──────────┼────────────────── ┼───────────┘
           │                   │
           ▼                   ▼
┌──────────────────┐  ┌────────────────────┐
│     Firebase     │  │   ML Predictor     │
│  Realtime DB     │  │  (Random Forest)   │
│  /temperatures   │  │   model.pkl        │
└──────────┬───────┘  └────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│           Web Dashboard (UI)             │
│   Gauge · Charts · Stats · Alerts · ML  │
└──────────────────────────────────────────┘
```

---

    ## 🚀 Quick Start

### Prerequisites

| Requirement | Detail |
|---|---|
| **Hardware** | ESP32 Dev Board + DHT22 Temperature Sensor |
| **Cloud** | Firebase project with Realtime Database enabled |
| **Cloud** | ThingSpeak channel (Channel ID + Read API Key) |
| **Email** | Gmail account + [App Password](https://myaccount.google.com/apppasswords) |
| **Software** | Python 3.9+, Arduino IDE |

---

### Step 1 — Clone & Install

```bash
git clone https://github.com/your-username/real-time-temp-monitoring-system.git
cd real-time-temp-monitoring-system
pip install -r requirements.txt
```

### Step 2 — Configure Environment

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Edit `.env` with your credentials:

```env
FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com
THINGSPEAK_CHANNEL_ID=your_channel_id
THINGSPEAK_READ_API_KEY=your_read_api_key
ALERT_EMAIL=your@gmail.com
ALERT_EMAIL_PASSWORD=your_gmail_app_password
TEMP_THRESHOLD=35.0
PREDICT_THRESHOLD=38.0
```

> **Gmail:** Use an [App Password](https://myaccount.google.com/apppasswords) — not your login password.

### Step 3 — Flash the ESP32

1. Open `arduino_sketch_with_alert_led.ino` in **Arduino IDE**
2. Set your **Wi-Fi SSID**, **Wi-Fi Password**, and **ThingSpeak Write API Key**
3. Connect **DHT22** to GPIO pin `4` (default)
4. Select board: **ESP32 Dev Module** → correct COM port
5. Click **Upload**

The ESP32 will push `temperature` + `humidity` to ThingSpeak every **60 seconds**.

### Step 4 — Train the ML Model

```bash
# Generate Indian IoT temperature training data
python data/generate_dataset.py

# Train the Random Forest model
python ml/train_model.py
```

Expected output:
```
  MAE  (Mean Absolute Error)  : 0.955 °C
  RMSE (Root Mean Sq. Error)  : 1.208 °C
  R2   (Coefficient of Det.)  : 0.9551
```

### Step 5 — Run the Flask Server

```bash
python app.py
```

```
============================================================
  ThingSpeak -> Firebase Bridge  (Background Thread Active)
  EMAIL ALERT SYSTEM ENABLED
============================================================
 * Running on http://127.0.0.1:5000
```

### Step 6 — Open Dashboard

Navigate to **[http://127.0.0.1:5000](http://127.0.0.1:5000)** 🎉

---

## 📁 Project Structure

```
real-time-temp-monitoring-system/
│
├── app.py                              # Flask backend + ThingSpeak→Firebase bridge
├── arduino_sketch_with_alert_led.ino  # ESP32 firmware (DHT22 + ThingSpeak)
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variable template
│
├── data/
│   ├── generate_dataset.py            # Indian IoT temperature dataset generator
│   └── iot_temp_india.csv             # Generated training dataset (2 years, hourly)
│
├── ml/
│   ├── train_model.py                 # Random Forest training script
│   ├── preprocess.py                  # Data cleaning + feature engineering pipeline
│   ├── model.pkl                      # Trained Random Forest model
│   └── scaler.pkl                     # MinMaxScaler for inference
│
├── utils/
│   ├── predictor.py                   # ML inference — predict_next_day()
│   └── alert_monitor.py              # Email alert logic (SMTP + cooldown)
│
└── templates/
    └── index.html                     # Dark-theme dashboard (Chart.js + SVG gauge)
```

---

## 🤖 ML Pipeline

The prediction system uses a **Random Forest Regressor** trained on realistic Indian indoor temperature data.

### Model Details

| Parameter | Value |
|---|---|
| Algorithm | `RandomForestRegressor` (scikit-learn) |
| Trees | 150 estimators |
| Max Depth | 12 |
| Features | `[temperature, hour, day_of_week, month, day_of_year]` |
| Target | `next_temperature` (next-step forecast) |
| Training Data | 17,520 hourly readings (Indian climate, 2022–2023) |
| **MAE** | **0.955°C** |
| **RMSE** | **1.208°C** |
| **R²** | **0.9551** |

### Feature Importances

```
temperature     ████████████████████  52.2%
day_of_year     ████████              20.0%
month           ███████               18.9%
hour            ████                   8.8%
day_of_week                            0.2%
```

### How to Retrain

```bash
python data/generate_dataset.py   # regenerate dataset
python ml/train_model.py          # retrain model
python app.py                     # restart server to load new model
```

---

## 🌐 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Main dashboard UI |
| `GET` | `/api/latest` | Latest sensor reading from memory |
| `GET` | `/api/history` | Last 24h of readings from Firebase |
| `GET` | `/predict` | ML temperature prediction + alert status |
| `GET` | `/api/alert-status` | Current alert system state |
| `GET` | `/api/alert-history` | List of all sent email alerts |
| `POST` | `/api/reset-alerts` | Reset alert cooldown (admin use) |

### Sample Response — `/api/latest`

```json
{
  "temperature": 34.2,
  "humidity": 61.5,
  "timestamp": "2024-04-24T14:05:00",
  "status": "Warm"
}
```

### Sample Response — `/predict`

```json
{
  "predicted_temp": 36.8,
  "alert": false,
  "alert_message": "Next-step forecast 36.8°C is within safe range (< 38°C).",
  "confidence": "±1.2°C",
  "model_loaded": true,
  "threshold": 38.0
}
```

---

## 🎨 Dashboard UI

| Feature | Detail |
|---|---|
| **Theme** | Dark — `#0D1117` background, `#161C27` cards |
| **Gauge** | 270° SVG arc, blue→green gradient, animated needle |
| **Charts** | Chart.js rolling 1-hour window, 4 × 15-min segments |
| **Stats Panel** | Min/Max for 1h / 6h / 24h from Firebase |
| **ML Panel** | Predicted next temperature + confidence interval |
| **Status Table** | Last 50 readings — `Normal` / `Warm` / `Alert` |

---

## 📧 Email Alert System

Alerts fire via Gmail SMTP when temperature exceeds `TEMP_THRESHOLD`:

- ✅ **3 automatic retries** on connection failure
- ✅ **Cooldown period** prevents alert spam
- ✅ **Alert history** accessible at `/api/alert-history`
- ✅ **Predictive alerts** — warns before threshold is hit using ML forecast

---

## ⚙️ Configuration Reference

| Variable | Default | Description |
|---|---|---|
| `FIREBASE_DATABASE_URL` | — | Firebase Realtime DB URL |
| `THINGSPEAK_CHANNEL_ID` | — | ThingSpeak channel number |
| `THINGSPEAK_READ_API_KEY` | — | ThingSpeak read API key |
| `ALERT_EMAIL` | — | Gmail address to send alerts from |
| `ALERT_EMAIL_PASSWORD` | — | Gmail App Password |
| `TEMP_THRESHOLD` | `35.0` | Alert trigger temperature (°C) |
| `PREDICT_THRESHOLD` | `38.0` | ML predictive alert threshold (°C) |

---

## 📋 Notes & Troubleshooting

| Issue | Solution |
|---|---|
| ESP32 won't connect | Ensure 2.4 GHz Wi-Fi (not 5 GHz) |
| Firebase permission denied | Enable unauthenticated read on `/temperatures` node |
| ThingSpeak not syncing | Verify `field1`=Temperature, `field2`=Humidity in channel |
| Email not sending | Use Gmail App Password, enable 2FA on Gmail account |
| Model predictions wrong | Retrain: `python data/generate_dataset.py && python ml/train_model.py` |
| Python encoding error | Run with: `python -X utf8 app.py` |

---

## 🛠️ Tech Stack

<p>
  <img src="https://img.shields.io/badge/ESP32-Espressif-red?style=flat-square&logo=espressif"/>
  <img src="https://img.shields.io/badge/Python-Flask-black?style=flat-square&logo=flask"/>
  <img src="https://img.shields.io/badge/Firebase-Realtime%20DB-orange?style=flat-square&logo=firebase"/>
  <img src="https://img.shields.io/badge/ThingSpeak-IoT%20Cloud-blue?style=flat-square"/>
  <img src="https://img.shields.io/badge/Scikit--Learn-ML-green?style=flat-square&logo=scikit-learn"/>
  <img src="https://img.shields.io/badge/Chart.js-Visualization-pink?style=flat-square"/>
  <img src="https://img.shields.io/badge/Gmail-SMTP%20Alerts-red?style=flat-square&logo=gmail"/>
</p>

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <p>Made with ❤️ | IoT + ML + Real-Time Data Engineering</p>
  <p>
    <a href="https://github.com/kuldeeprathod1305">@kuldeeprathod1305</a>
  </p>
</div>
