```
╔════════════════════════════════════════════════════════════════════╗
║     🔮 TEMPERATURE PREDICTION API - QUICK REFERENCE GUIDE           ║
╚════════════════════════════════════════════════════════════════════╝
```

# Temperature Prediction API Reference

## 🚀 Quick Start

```bash
# Single prediction (30 min ahead)
curl "http://127.0.0.1:5000/api/predict"

# Multiple predictions
curl "http://127.0.0.1:5000/api/predict/multiple"

# 24-hour forecast
curl "http://127.0.0.1:5000/api/predict/24h-forecast"

# Moving average (smoothed data)
curl "http://127.0.0.1:5000/api/predict/moving-average"

# Anomaly detection
curl "http://127.0.0.1:5000/api/predict/anomalies"
```

---

## 📡 API Endpoints

### 1️⃣ Single Prediction

**Endpoint:** `GET /api/predict`

**Purpose:** Predict temperature for a specific time in the future

**Parameters:**
| Name | Type | Default | Example |
|------|------|---------|---------|
| `minutes_ahead` | int | 30 | 60 |

**cURL Example:**
```bash
curl "http://127.0.0.1:5000/api/predict?minutes_ahead=60"
```

**Response:**
```json
{
  "status": "success",
  "prediction": {
    "predicted_temperature": 32.75,
    "prediction_time": "2026-03-27T14:30:00+05:30",
    "minutes_ahead": 30,
    "confidence_percentage": 87.45,
    "model_slope": 0.0125,
    "last_recorded_temp": 32.1,
    "last_recorded_time": "2026-03-27T14:00:00+05:30"
  },
  "data_points_used": 240
}
```

**JavaScript Example:**
```javascript
async function predictTemperature(minutes = 30) {
    const response = await fetch(`/api/predict?minutes_ahead=${minutes}`);
    const data = await response.json();
    
    if (data.status === 'success') {
        const pred = data.prediction;
        console.log(`In ${pred.minutes_ahead} minutes: ${pred.predicted_temperature}°C`);
        console.log(`Confidence: ${pred.confidence_percentage}%`);
    }
}

predictTemperature(60); // Predict 60 minutes ahead
```

---

### 2️⃣ Multiple Predictions

**Endpoint:** `GET /api/predict/multiple`

**Purpose:** Get predictions for multiple time intervals

**Parameters:**
| Name | Type | Default | Example |
|------|------|---------|---------|
| `intervals` | string | "15,30,60,120" | "10,30,120" |

**cURL Example:**
```bash
# Default intervals (15, 30, 60, 120 minutes)
curl "http://127.0.0.1:5000/api/predict/multiple"

# Custom intervals
curl "http://127.0.0.1:5000/api/predict/multiple?intervals=5,15,30,60,180"
```

**Response:**
```json
{
  "status": "success",
  "predictions_data": {
    "predictions": [
      {
        "predicted_temperature": 32.23,
        "prediction_time": "2026-03-27T14:15:00+05:30",
        "minutes_ahead": 15,
        "confidence_percentage": 87.45
      },
      {
        "predicted_temperature": 32.50,
        "prediction_time": "2026-03-27T14:30:00+05:30",
        "minutes_ahead": 30,
        "confidence_percentage": 87.45
      },
      // ... more predictions
    ],
    "trend_direction": "↗️ Increasing"
  },
  "data_points_used": 240
}
```

**JavaScript Example:**
```javascript
async function getPredictions() {
    const intervals = "15,30,60,120,240"; // 15min, 30min, 1h, 2h, 4h
    const response = await fetch(`/api/predict/multiple?intervals=${intervals}`);
    const data = await response.json();
    
    const preds = data.predictions_data.predictions;
    preds.forEach(p => {
        console.log(`+${p.minutes_ahead}min: ${p.predicted_temperature}°C (${p.confidence_percentage}%)`);
    });
}
```

---

### 3️⃣ 24-Hour Forecast

**Endpoint:** `GET /api/predict/24h-forecast`

**Purpose:** Get hourly temperature predictions for next 24 hours

**Parameters:** None

**cURL Example:**
```bash
curl "http://127.0.0.1:5000/api/predict/24h-forecast"
```

**Response:**
```json
{
  "status": "success",
  "forecast_24h": {
    "hourly_forecast": [
      {
        "hour": 1,
        "predicted_temperature": 32.25,
        "confidence_percentage": 87.45,
        "time": "2026-03-27T15:00:00+05:30"
      },
      {
        "hour": 2,
        "predicted_temperature": 32.45,
        "confidence_percentage": 87.45,
        "time": "2026-03-27T16:00:00+05:30"
      },
      // ... 22 more hours
    ],
    "summary": {
      "predicted_max": 35.25,
      "predicted_min": 29.85,
      "predicted_avg": 32.45,
      "max_hour": 14,
      "min_hour": 6
    },
    "trend_24h": "↗️ Warming trend"
  },
  "data_points_used": 240
}
```

**JavaScript Example:**
```javascript
async function get24hForecast() {
    const response = await fetch('/api/predict/24h-forecast');
    const data = await response.json();
    
    const forecast = data.forecast_24h;
    const summary = forecast.summary;
    
    console.log(`Tomorrow's forecast:`);
    console.log(`  Max: ${summary.predicted_max}°C at Hour ${summary.max_hour}`);
    console.log(`  Min: ${summary.predicted_min}°C at Hour ${summary.min_hour}`);
    console.log(`  Avg: ${summary.predicted_avg}°C`);
    console.log(`  ${forecast.trend_24h}`);
}
```

---

### 4️⃣ Moving Average

**Endpoint:** `GET /api/predict/moving-average`

**Purpose:** Get smoothed temperature data (noise reduction)

**Parameters:**
| Name | Type | Default | Example |
|------|------|---------|---------|
| `window` | int | 5 | 10 |

**cURL Example:**
```bash
# Default window (5 readings)
curl "http://127.0.0.1:5000/api/predict/moving-average"

# Larger window for more smoothing
curl "http://127.0.0.1:5000/api/predict/moving-average?window=10"
```

**Response:**
```json
{
  "status": "success",
  "moving_average": [
    {
      "timestamp": "2026-03-27T10:00:00Z",
      "temperature": 31.50,
      "window_size": 1
    },
    {
      "timestamp": "2026-03-27T10:01:00Z",
      "temperature": 31.55,
      "window_size": 2
    },
    // ... more data
  ],
  "window_size": 5,
  "data_points": 240
}
```

**JavaScript Example:**
```javascript
async function getSmoothedData(window = 5) {
    const response = await fetch(`/api/predict/moving-average?window=${window}`);
    const data = await response.json();
    
    const ma_data = data.moving_average;
    console.log(`Smoothed data with window=${window}:`);
    
    // Plot or display last 10 points
    ma_data.slice(-10).forEach(point => {
        console.log(`${point.timestamp}: ${point.temperature}°C`);
    });
}
```

---

### 5️⃣ Anomaly Detection

**Endpoint:** `GET /api/predict/anomalies`

**Purpose:** Detect unusual temperature readings

**Parameters:**
| Name | Type | Default | Example |
|------|------|---------|---------|
| `threshold_std` | float | 2.0 | 1.5 |

**cURL Example:**
```bash
# Default threshold (2 standard deviations)
curl "http://127.0.0.1:5000/api/predict/anomalies"

# Stricter threshold
curl "http://127.0.0.1:5000/api/predict/anomalies?threshold_std=1.5"
```

**Response:**
```json
{
  "status": "success",
  "anomaly_analysis": {
    "mean_temperature": 32.10,
    "std_deviation": 1.25,
    "anomaly_threshold": 2.50,
    "anomalies_detected": 3,
    "anomalies": [
      {
        "index": 45,
        "temperature": 37.80,
        "timestamp": "2026-03-27T10:45:00Z",
        "deviation": 5.70,
        "std_devs_away": 4.56
      },
      // ... more anomalies
    ]
  }
}
```

**JavaScript Example:**
```javascript
async function detectAnomalies(threshold = 2.0) {
    const response = await fetch(`/api/predict/anomalies?threshold_std=${threshold}`);
    const data = await response.json();
    
    const analysis = data.anomaly_analysis;
    console.log(`Mean: ${analysis.mean_temperature}°C ± ${analysis.std_deviation}°C`);
    console.log(`Anomalies found: ${analysis.anomalies_detected}`);
    
    analysis.anomalies.forEach(anom => {
        console.log(`🚨 ${anom.timestamp}: ${anom.temperature}°C (${anom.std_devs_away}σ)`);
    });
}
```

---

## 🧠 Understanding Responses

### Confidence Percentage

| Score | Reliability | Meaning |
|-------|-------------|---------|
| 90-100% | ⭐⭐⭐⭐⭐ | Very reliable, stable trend |
| 75-90% | ⭐⭐⭐⭐ | Reliable, slight variations |
| 60-75% | ⭐⭐⭐ | Moderate, significant variations |
| 50-60% | ⭐⭐ | Low, high variability |
| <50% | ⭐ | Very low, chaotic pattern |

### Model Slope

- **Positive value** (e.g., 0.015) → Temperature increasing ~0.015°C per minute
- **Negative value** (e.g., -0.008) → Temperature decreasing ~0.008°C per minute
- **Near zero** → Temperature relatively stable

### Trend Direction

- `↗️ Increasing` — Temperature getting hotter
- `↘️ Decreasing` — Temperature getting cooler

---

## 🔧 Python Integration Examples

### Example 1: Predictive Alert

```python
import requests

def send_alert_if_temp_will_exceed(threshold=35.0, advance_minutes=30):
    """Send alert if temperature will exceed threshold"""
    response = requests.get(
        f"http://127.0.0.1:5000/api/predict?minutes_ahead={advance_minutes}"
    )
    data = response.json()
    
    if data['status'] == 'success':
        pred_temp = data['prediction']['predicted_temperature']
        confidence = data['prediction']['confidence_percentage']
        
        if pred_temp > threshold and confidence > 70:
            print(f"⚠️  ALERT: Temperature will reach {pred_temp}°C in {advance_minutes} minutes!")
            # Send email/SMS here
            return True
    
    return False
```

### Example 2: Optimal Time Finder

```python
def find_coolest_time_today():
    """Find the coolest hour in next 24 hours"""
    response = requests.get("http://127.0.0.1:5000/api/predict/24h-forecast")
    data = response.json()
    
    forecast = data['forecast_24h']
    hourly = forecast['hourly_forecast']
    
    coolest = min(hourly, key=lambda x: x['predicted_temperature'])
    
    print(f"Coolest time today: Hour {coolest['hour']} at {coolest['predicted_temperature']}°C")
    print(f"Prediction time: {coolest['time']}")
    
    return coolest
```

### Example 3: Data Quality Check

```python
def check_data_quality():
    """Check for anomalies indicating bad sensor"""
    response = requests.get("http://127.0.0.1:5000/api/predict/anomalies?threshold_std=2.0")
    data = response.json()
    
    analysis = data['anomaly_analysis']
    
    if analysis['anomalies_detected'] > 10:
        print("⚠️  Many anomalies detected - sensor may be faulty!")
        return False
    
    std_dev = analysis['std_deviation']
    if std_dev > 5.0:
        print("⚠️  High variability - check environment for disturbances")
        return False
    
    print("✅ Data quality looks good")
    return True
```

---

## 📊 Dashboard Integration

### Chart.js Example

```javascript
async function plotPredictions() {
    // Get 24-hour forecast
    const response = await fetch('/api/predict/24h-forecast');
    const data = await response.json();
    
    const forecast = data.forecast_24h.hourly_forecast;
    
    // Prepare chart data
    const labels = forecast.map(h => `Hour ${h.hour}`);
    const temps = forecast.map(h => h.predicted_temperature);
    
    // Create chart
    const ctx = document.getElementById('predictionChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Predicted Temperature (24h)',
                data: temps,
                borderColor: '#3B82F6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                fill: true,
                tension: 0.4
            }]
        }
    });
}
```

---

## ⚠️ Error Handling

All endpoints return errors with HTTP status codes:

```javascript
async function predictWithErrorHandling() {
    try {
        const response = await fetch('/api/predict?minutes_ahead=30');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
            console.log(data.prediction);
        } else {
            console.error('API Error:', data.error);
        }
    } catch (error) {
        console.error('Network Error:', error);
    }
}
```

---

## 📝 Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "Insufficient historical data" | <10 data points | Wait 10 minutes with system running |
| Low confidence (<50%) | Chaotic temperature pattern | Check environment for disruptions |
| Predictions seem wrong | Bad data quality | Use `/api/predict/anomalies` to check |
| Connection refused | Flask server not running | Start with `python app.py` |

---

**🔮 Start predicting temperatures with confidence!**
