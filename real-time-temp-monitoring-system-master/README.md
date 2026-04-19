# Real-Time Temperature & Humidity Monitoring System

A production-grade IoT dashboard built with an **ESP32 + DHT22 sensor**, **Firebase Realtime Database**, and a **Flask** backend. Features a fully redesigned dark-theme web dashboard with live charts, temperature gauge, historical statistics, and email alerting.

---

## 🚀 How to Run Everything

Follow these steps in order to get the full system running end-to-end.

### Step 1 — Clone the repo & install dependencies

```bash
cd real-time-temp-monitoring-system-master
pip install -r requirements.txt
```

### Step 2 — Configure your environment

Copy `.env.example` to `.env`, then fill in your credentials:

```bash
copy .env.example .env   # Windows
# or
cp .env.example .env     # macOS / Linux
```

Open `.env` and set:

```env
FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com
THINGSPEAK_CHANNEL_ID=your_channel_id
THINGSPEAK_READ_API_KEY=your_read_key
ALERT_EMAIL=your@gmail.com
ALERT_EMAIL_PASSWORD=your_gmail_app_password
TEMP_THRESHOLD=35.0
```

> **Gmail note:** Use a [Gmail App Password](https://myaccount.google.com/apppasswords), not your regular password.

### Step 3 — Flash the ESP32

1. Open `arduino_sketch_with_alert_led.ino` in the **Arduino IDE**.
2. Set your **Wi-Fi SSID**, **Wi-Fi Password**, and **ThingSpeak Write API Key** inside the sketch.
3. Connect your **DHT22** to the correct GPIO pin (default: `4`).
4. Select your board (**ESP32 Dev Module**) and the right COM port.
5. Click **Upload**.

The ESP32 will start sending temperature + humidity to **ThingSpeak** every 60 seconds automatically.

### Step 4 — Start the Flask server

```bash
python -X utf8 app.py
```

You should see:

```
============================================================
  ThingSpeak -> Firebase Bridge (Background Thread Restored)
  ✨ EMAIL ALERT SYSTEM ENABLED
============================================================
 * Running on http://127.0.0.1:5000
 * Running on http://0.0.0.0:5000
```

The server does two things at once:
- **Background thread** — polls ThingSpeak every 60 s and pushes new readings to Firebase
- **Web server** — serves the dashboard and REST API

### Step 5 — Open the Dashboard

Go to **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

The dashboard will:
1. Fetch the last **24 hours** of history from Firebase on load
2. Populate the gauge, charts, stats, and table immediately
3. Auto-refresh the latest reading every **60 seconds**

---

## 🖼️ Dashboard Preview

The redesigned dashboard includes:
- **Big circular temperature gauge** — animated SVG ring with blue→green gradient
- **Live trend charts** — 1-hour rolling window, 4 × 15-minute segments
- **Device status panel** — online/offline, last updated, uptime
- **Historical stats** — Min/Max for last 1h / 6h / 24h pulled from Firebase
- **Recent readings table** — timestamped rows with Normal/Warm/Alert status

---

## ✨ Features

- 📡 **ESP32 + DHT22** — collects temperature & humidity every 60 seconds
- ☁️ **ThingSpeak → Firebase bridge** — background Flask thread syncs data to Firebase Realtime Database
- 🌡️ **Animated gauge** — 270° SVG arc with smooth transitions, color-coded by temperature
- 📊 **Trend charts** — Chart.js line charts divided into 4 equal 15-minute segments
- 📧 **Email alerts** — automatic Gmail alerts when temperature exceeds threshold
- 🔄 **Real-time polling** — dashboard refreshes every 60 seconds via `/api/latest`
- 📜 **History endpoint** — `/api/history` fetches last 24h of data from Firebase for stats

---

## 🗂️ Project Structure

```
├── app.py                          # Flask backend + ThingSpeak→Firebase bridge
├── arduino_sketch_with_alert_led.ino  # ESP32 firmware
├── requirements.txt                # Python dependencies
├── templates/
│   ├── index.html                  # Redesigned dark dashboard UI
│   └── style.css                   # Legacy styles (superseded by inline Tailwind CSS)
├── utils/
│   └── alert_monitor.py            # Email alert logic
└── .env                            # Environment variables (not committed)
```

---

## 🔌 Prerequisites

| Requirement | Detail |
|---|---|
| Hardware | ESP32 board + DHT22 sensor |
| Cloud | Firebase Realtime Database project |
| Cloud | ThingSpeak channel (Channel ID + Read API Key) |
| Email | Gmail account with App Password for alerts |
| Software | Python 3.9+, pip |

---

## ⚙️ Setup & Configuration

### 1. Clone & Install

```bash
cd real-time-temp-monitoring-system-master
pip install -r requirements.txt
```

### 2. Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```env
FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com
THINGSPEAK_CHANNEL_ID=your_channel_id
THINGSPEAK_READ_API_KEY=your_read_key
ALERT_EMAIL=your@gmail.com
ALERT_EMAIL_PASSWORD=your_app_password
TEMP_THRESHOLD=35.0
```

### 3. Arduino Setup

1. Open `arduino_sketch_with_alert_led.ino` in Arduino IDE.
2. Set your Wi-Fi SSID, password, and ThingSpeak Write API Key inside the sketch.
3. Upload to your ESP32 board.

### 4. Run the Flask Server

```bash
python -X utf8 app.py
```

> **Note:** The `-X utf8` flag ensures emoji characters in logs display correctly on Windows.

### 5. Open the Dashboard

Navigate to **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Main dashboard UI |
| `GET` | `/api/latest` | Latest sensor reading from memory |
| `GET` | `/api/history` | Last 24h of readings from Firebase |
| `GET` | `/api/alert-status` | Current alert system state |
| `GET` | `/api/alert-history` | List of all sent alerts |
| `POST` | `/api/reset-alerts` | Reset alert cooldown (admin) |

---

## 📊 How Data Flows

```
ESP32 + DHT22
    │  (every 60s via Wi-Fi)
    ▼
ThingSpeak Channel
    │  (Flask background thread polls every 60s)
    ▼
Firebase Realtime Database  (/temperatures)
    │  (browser fetches on load + every 60s)
    ▼
Flask /api/latest  &  /api/history
    │
    ▼
Dashboard UI  →  Gauge + Charts + Stats + Table
```

---

## 🎨 Dashboard UI Highlights

- **Theme:** Soft dark (`#0D1117` bg, `#161C27` cards)
- **Colors:** Blue `#3B82F6` (temp) + Green `#10B981` (humidity/live)
- **Gauge:** 270° SVG arc, blue→green gradient; white dot tracks current value
- **Charts:** 1-hour rolling window split into **4 × 15-minute segments** on X-axis
- **Stats:** Min/Max computed from Firebase history (1h / 6h / 24h buckets)
- **Table:** Last 50 readings; status = Normal / Warm (≥30°C) / Alert (≥35°C)

---

## 📧 Email Alert System

Alerts are sent via Gmail SMTP when temperature exceeds the configured threshold:
- 3 automatic retries on failure
- Cooldown period to avoid alert spam
- Alert history accessible via `/api/alert-history`

---

## 📝 Notes

- Ensure your ESP32 connects to a **2.4 GHz** Wi-Fi network (not 5 GHz).
- Firebase rules must allow **unauthenticated read** for the `/temperatures` node (or configure auth accordingly).
- The ThingSpeak channel must have `field1` = Temperature, `field2` = Humidity.
- For production, replace the Flask dev server with **Gunicorn** or **uWSGI**.
