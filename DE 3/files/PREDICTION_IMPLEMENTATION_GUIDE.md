# 🔮 Temperature Prediction Feature Implementation Guide

## Overview

This guide explains how to add temperature prediction functionality to your Real-Time Temperature & Humidity Monitoring System. The system uses **Linear Regression** combined with **moving averages** to predict future temperatures with confidence scores.

---

## 📋 What's New

### New Features

1. **🔮 Temperature Prediction** — Predict temperature for any time interval (15 min, 30 min, 1 hour, etc.)
2. **📊 24-Hour Forecast** — Hourly temperature predictions for the next 24 hours
3. **📈 Moving Average** — Smoothed temperature data to reduce noise
4. **🚨 Anomaly Detection** — Identify unusual temperature readings
5. **📉 Trend Analysis** — Understand if temperature is warming or cooling
6. **🎯 Confidence Scores** — Get prediction reliability metrics

### New API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/predict` | GET | Single temperature prediction |
| `/api/predict/multiple` | GET | Multiple predictions at different intervals |
| `/api/predict/24h-forecast` | GET | Hourly forecast for 24 hours |
| `/api/predict/moving-average` | GET | Smoothed temperature data |
| `/api/predict/anomalies` | GET | Anomaly detection analysis |

---

## 🚀 Installation Steps

### Step 1: Update Requirements

Replace your `requirements.txt` with the updated version:

```txt
requests==2.31.0
Flask==3.0.3
python-dotenv==1.0.0
scikit-learn==1.3.2
numpy==1.24.3
```

Then install the new dependencies:

```bash
pip install -r requirements.txt
```

### Step 2: Add Predictor Module

Copy the `temperature_predictor.py` file to your `utils/` directory:

```
your-project/
├── utils/
│   ├── __init__.py
│   ├── alert_monitor.py
│   ├── email_config.py
│   └── temperature_predictor.py  ← NEW FILE
├── app.py
└── requirements.txt
```

### Step 3: Update utils/__init__.py

Add these imports to `utils/__init__.py`:

```python
from utils.temperature_predictor import TemperaturePredictor, temperature_predictor

__all__ = [
    # ... existing exports ...
    "TemperaturePredictor",
    "temperature_predictor"
]
```

### Step 4: Update app.py

Replace your `app.py` with the updated version that includes:

```python
from utils.temperature_predictor import temperature_predictor
```

And add all the new prediction endpoints (see below for details).

---

## 📡 API Endpoint Usage

### 1. Single Temperature Prediction

Predict temperature for a specific time in the future.

```bash
# Predict temperature 30 minutes ahead
curl "http://127.0.0.1:5000/api/predict?minutes_ahead=30"
```

**Response:**

```json
{
  "status": "success",
  "prediction": {
    "predicted_temperature": 32.5,
    "prediction_time": "2026-03-27T14:30:00+05:30",
    "minutes_ahead": 30,
    "confidence_percentage": 87.5,
    "model_slope": 0.0125,
    "last_recorded_temp": 32.1,
    "last_recorded_time": "2026-03-27T14:00:00+05:30"
  },
  "data_points_used": 240
}
```

**Parameters:**

- `minutes_ahead` (int, default: 30) — Minutes into future to predict

---

### 2. Multiple Predictions

Get predictions for multiple time intervals at once.

```bash
# Get predictions for 15, 30, 60, and 120 minutes ahead
curl "http://127.0.0.1:5000/api/predict/multiple"

# Custom intervals
curl "http://127.0.0.1:5000/api/predict/multiple?intervals=10,20,40,60"
```

**Response:**

```json
{
  "status": "success",
  "predictions_data": {
    "predictions": [
      {
        "predicted_temperature": 32.3,
        "prediction_time": "2026-03-27T14:15:00+05:30",
        "minutes_ahead": 15,
        "confidence_percentage": 87.5
      },
      {
        "predicted_temperature": 32.5,
        "prediction_time": "2026-03-27T14:30:00+05:30",
        "minutes_ahead": 30,
        "confidence_percentage": 87.5
      },
      // ... more predictions
    ],
    "trend_direction": "↗️ Increasing"
  },
  "data_points_used": 240
}
```

**Parameters:**

- `intervals` (string, default: "15,30,60,120") — Comma-separated minute values

---

### 3. 24-Hour Forecast

Get hourly temperature predictions for the next 24 hours.

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
        "predicted_temperature": 32.3,
        "confidence_percentage": 87.5,
        "time": "2026-03-27T15:00:00+05:30"
      },
      {
        "hour": 2,
        "predicted_temperature": 32.45,
        "confidence_percentage": 87.5,
        "time": "2026-03-27T16:00:00+05:30"
      },
      // ... 22 more hours
    ],
    "summary": {
      "predicted_max": 35.2,
      "predicted_min": 29.8,
      "predicted_avg": 32.5,
      "max_hour": 14,
      "min_hour": 6
    },
    "trend_24h": "↗️ Warming trend"
  },
  "data_points_used": 240
}
```

---

### 4. Moving Average (Smoothed Data)

Get temperature data smoothed with moving average to reduce noise.

```bash
# Default window size of 5 readings
curl "http://127.0.0.1:5000/api/predict/moving-average"

# Custom window size
curl "http://127.0.0.1:5000/api/predict/moving-average?window=10"
```

**Response:**

```json
{
  "status": "success",
  "moving_average": [
    {
      "timestamp": "2026-03-27T10:00:00Z",
      "temperature": 31.5,
      "window_size": 1
    },
    {
      "timestamp": "2026-03-27T10:01:00Z",
      "temperature": 31.55,
      "window_size": 2
    },
    // ... more data points
  ],
  "window_size": 5,
  "data_points": 240
}
```

**Parameters:**

- `window` (int, default: 5) — Window size for moving average

---

### 5. Anomaly Detection

Detect unusual temperature readings in your data.

```bash
# Default threshold of 2 standard deviations
curl "http://127.0.0.1:5000/api/predict/anomalies"

# Custom threshold
curl "http://127.0.0.1:5000/api/predict/anomalies?threshold_std=1.5"
```

**Response:**

```json
{
  "status": "success",
  "anomaly_analysis": {
    "mean_temperature": 32.1,
    "std_deviation": 1.25,
    "anomaly_threshold": 2.5,
    "anomalies_detected": 3,
    "anomalies": [
      {
        "index": 45,
        "temperature": 37.8,
        "timestamp": "2026-03-27T10:45:00Z",
        "deviation": 5.7,
        "std_devs_away": 4.56
      },
      // ... more anomalies
    ]
  }
}
```

**Parameters:**

- `threshold_std` (float, default: 2.0) — Standard deviations for anomaly threshold

---

## 🧠 How the Prediction Works

### Algorithm: Linear Regression

The system uses **linear regression** from scikit-learn to model the temperature trend:

1. **Data Preparation**: Extracts timestamps and temperatures from Firebase
2. **Time Conversion**: Converts timestamps to minutes since first reading
3. **Model Training**: Fits a linear equation: `Temperature = slope × time + intercept`
4. **Prediction**: Uses the trained model to predict future temperatures
5. **Confidence**: Calculates R² score (0-100%) to show prediction reliability

### Confidence Scores

- **85-100%**: Very reliable predictions (stable trend)
- **70-85%**: Reliable predictions (moderate variations)
- **50-70%**: Moderate reliability (high variations)
- **<50%**: Low reliability (chaotic/random patterns)

### Trend Analysis

- **Positive slope (↗️)**: Temperature increasing over time
- **Negative slope (↘️)**: Temperature decreasing over time

---

## 🎨 Dashboard Integration Example

Add prediction data to your dashboard:

```javascript
// Fetch 24-hour forecast
async function loadForecast() {
    const response = await fetch('/api/predict/24h-forecast');
    const data = await response.json();
    
    if (data.status === 'success') {
        const forecast = data.forecast_24h;
        
        // Update UI with forecast data
        console.log("Max temp today:", forecast.summary.predicted_max);
        console.log("Min temp today:", forecast.summary.predicted_min);
        console.log("Trend:", forecast.trend_24h);
        
        // Plot hourly predictions
        const temps = forecast.hourly_forecast.map(h => h.predicted_temperature);
        // ... render chart
    }
}

// Fetch next 30-minute prediction
async function loadPrediction() {
    const response = await fetch('/api/predict?minutes_ahead=30');
    const data = await response.json();
    
    if (data.status === 'success') {
        const pred = data.prediction;
        console.log(`In 30 min: ${pred.predicted_temperature}°C (${pred.confidence_percentage}% confident)`);
    }
}
```

---

## 🧪 Testing the Prediction System

### Test Script

Create `test_prediction.py`:

```python
"""
Test Temperature Prediction System
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_single_prediction():
    """Test single temperature prediction"""
    print("\n" + "="*60)
    print("TEST 1: Single Prediction (30 minutes ahead)")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/predict?minutes_ahead=30")
    data = response.json()
    
    if data['status'] == 'success':
        pred = data['prediction']
        print(f"✅ Predicted Temperature: {pred['predicted_temperature']}°C")
        print(f"✅ Confidence: {pred['confidence_percentage']}%")
        print(f"✅ Predicted Time: {pred['prediction_time']}")
        print(f"✅ Data Points Used: {data['data_points_used']}")
    else:
        print(f"❌ Error: {data.get('error')}")

def test_multiple_predictions():
    """Test multiple predictions"""
    print("\n" + "="*60)
    print("TEST 2: Multiple Predictions")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/predict/multiple?intervals=15,30,60,120")
    data = response.json()
    
    if data['status'] == 'success':
        preds = data['predictions_data']['predictions']
        print(f"✅ Generated {len(preds)} predictions")
        print(f"✅ Trend: {data['predictions_data']['trend_direction']}")
        for pred in preds:
            print(f"   • +{pred['minutes_ahead']}min: {pred['predicted_temperature']}°C ({pred['confidence_percentage']}%)")
    else:
        print(f"❌ Error: {data.get('error')}")

def test_24h_forecast():
    """Test 24-hour forecast"""
    print("\n" + "="*60)
    print("TEST 3: 24-Hour Forecast")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/predict/24h-forecast")
    data = response.json()
    
    if data['status'] == 'success':
        forecast = data['forecast_24h']
        summary = forecast['summary']
        print(f"✅ 24-Hour Forecast Generated")
        print(f"   • Max: {summary['predicted_max']}°C (Hour {summary['max_hour']})")
        print(f"   • Min: {summary['predicted_min']}°C (Hour {summary['min_hour']})")
        print(f"   • Avg: {summary['predicted_avg']}°C")
        print(f"   • Trend: {forecast['trend_24h']}")
    else:
        print(f"❌ Error: {data.get('error')}")

def test_moving_average():
    """Test moving average"""
    print("\n" + "="*60)
    print("TEST 4: Moving Average")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/predict/moving-average?window=5")
    data = response.json()
    
    if data['status'] == 'success':
        ma = data['moving_average']
        print(f"✅ Generated {len(ma)} moving average data points")
        print(f"✅ Window Size: {data['window_size']}")
        # Show last 5
        print("   Latest readings:")
        for point in ma[-5:]:
            print(f"   • {point['timestamp']}: {point['temperature']}°C")
    else:
        print(f"❌ Error: {data.get('error')}")

def test_anomaly_detection():
    """Test anomaly detection"""
    print("\n" + "="*60)
    print("TEST 5: Anomaly Detection")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/predict/anomalies?threshold_std=2.0")
    data = response.json()
    
    if data['status'] == 'success':
        analysis = data['anomaly_analysis']
        print(f"✅ Mean Temperature: {analysis['mean_temperature']}°C")
        print(f"✅ Std Deviation: {analysis['std_deviation']}°C")
        print(f"✅ Anomalies Detected: {analysis['anomalies_detected']}")
        
        if analysis['anomalies']:
            print("   Top anomalies:")
            for anom in analysis['anomalies'][:3]:
                print(f"   • {anom['timestamp']}: {anom['temperature']}°C ({anom['std_devs_away']:.2f}σ)")
    else:
        print(f"❌ Error: {data.get('error')}")

if __name__ == "__main__":
    print("\n🔮 TEMPERATURE PREDICTION SYSTEM - TEST SUITE\n")
    
    test_single_prediction()
    test_multiple_predictions()
    test_24h_forecast()
    test_moving_average()
    test_anomaly_detection()
    
    print("\n" + "="*60)
    print("✅ TESTING COMPLETE")
    print("="*60 + "\n")
```

Run it:

```bash
python test_prediction.py
```

---

## 📊 Example Use Cases

### Use Case 1: Alert Before Threshold

```python
# Predict temperature 1 hour ahead
# If predicted temp > threshold, send warning 1 hour early

response = requests.get("http://127.0.0.1:5000/api/predict?minutes_ahead=60")
pred = response.json()['prediction']

if pred['predicted_temperature'] > 35:
    send_warning_email(f"Temperature will exceed threshold in 1 hour")
```

### Use Case 2: Optimal Operating Times

```python
# Get 24-hour forecast to find coolest times

response = requests.get("http://127.0.0.1:5000/api/predict/24h-forecast")
forecast = response.json()['forecast_24h']

# Find hour with lowest temperature
coolest_hour = min(
    forecast['hourly_forecast'],
    key=lambda x: x['predicted_temperature']
)
print(f"Coolest time: Hour {coolest_hour['hour']} at {coolest_hour['predicted_temperature']}°C")
```

### Use Case 3: Anomaly Alerts

```python
# Check for anomalies that might indicate sensor malfunction

response = requests.get("http://127.0.0.1:5000/api/predict/anomalies")
analysis = response.json()['anomaly_analysis']

if analysis['anomalies_detected'] > 5:
    print("⚠️ Many anomalies detected - check sensor!")
```

---

## ⚙️ Configuration & Tuning

### Minimum Data Requirements

The prediction model needs at least **10 data points** to work. With a 60-second polling interval, this takes ~10 minutes of operation.

### Improving Predictions

1. **More Data**: Collect 24+ hours for better trend detection
2. **Stable Environment**: Consistent ambient conditions improve accuracy
3. **Window Size**: Adjust moving average window (default: 5) for smoother/noisier data
4. **Anomaly Threshold**: Adjust std deviation threshold for anomaly detection

---

## 🐛 Troubleshooting

### "Insufficient data for prediction"

- **Cause**: Less than 10 historical data points
- **Solution**: Wait 10 minutes with the system running, then retry

### "Low confidence percentage"

- **Cause**: Chaotic or highly variable temperature patterns
- **Solution**: Check for external factors causing variations (doors opening, fan running, etc.)

### Predictions seem wrong

- **Cause**: Linear regression assumes linear trend; non-linear patterns won't be captured
- **Solution**: Check if temperature follows a predictable pattern
- **Alternative**: Use moving average to smoothify noisy data first

---

## 📝 Summary of Changes

| File | Changes |
|------|---------|
| `requirements.txt` | Added: scikit-learn, numpy |
| `app.py` | Added 5 new prediction endpoints |
| `utils/__init__.py` | Added: temperature_predictor imports |
| **NEW** `utils/temperature_predictor.py` | Complete prediction system |

---

## 🎯 Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Copy `temperature_predictor.py` to `utils/` folder
3. ✅ Update `app.py` with new endpoints
4. ✅ Update `utils/__init__.py` with imports
5. ✅ Run `python test_prediction.py` to verify
6. ✅ Access predictions via `/api/predict` endpoints

---

## 📞 Support & Issues

For issues or questions:
1. Check that all dependencies are installed: `pip list | grep scikit-learn`
2. Verify Firebase has historical data (at least 10 readings)
3. Check Flask logs for error messages
4. Ensure timestamps in Firebase are in ISO format

---

**🔮 Happy Predicting! Your temperature monitoring system is now even smarter.**
