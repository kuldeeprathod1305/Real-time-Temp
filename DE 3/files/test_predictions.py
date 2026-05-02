#!/usr/bin/env python3
"""
🔮 Temperature Prediction System - Test Script
Run this after starting Flask to verify all endpoints work.

Usage:
    python test_predictions.py
"""

import requests
import json
import time
from datetime import datetime

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {text}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.ENDC}")

BASE_URL = "http://127.0.0.1:5000"

def check_server():
    """Check if Flask server is running"""
    print_header("Checking Flask Server")
    
    try:
        response = requests.get(f"{BASE_URL}/api/latest", timeout=5)
        if response.status_code == 200:
            print_success("Flask server is running and responding")
            return True
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to Flask server")
        print_info("Make sure Flask is running:")
        print("  python -X utf8 app.py")
        return False
    except Exception as e:
        print_error(f"Error connecting to server: {e}")
        return False

def test_endpoint(name, endpoint, params=None, description=""):
    """Test a single API endpoint"""
    print(f"\n{Colors.BOLD}Test: {name}{Colors.ENDC}")
    if description:
        print(f"Description: {description}")
    print(f"Endpoint: GET {endpoint}")
    
    if params:
        print(f"Parameters: {params}")
    
    try:
        url = f"{BASE_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                print_success("Endpoint responded successfully")
                return True, data
            else:
                error_msg = data.get('error', 'Unknown error')
                print_error(f"API returned error: {error_msg}")
                return False, data
        else:
            print_error(f"HTTP {response.status_code}: {response.text}")
            return False, None
    
    except requests.exceptions.Timeout:
        print_error("Request timed out (10 seconds)")
        return False, None
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server")
        return False, None
    except json.JSONDecodeError:
        print_error("Response is not valid JSON")
        return False, None
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False, None

def test_single_prediction():
    """Test /api/predict endpoint"""
    print_header("TEST 1: Single Prediction")
    
    success, data = test_endpoint(
        "Single Prediction (30 minutes ahead)",
        "/api/predict",
        params={'minutes_ahead': 30},
        description="Predicts temperature 30 minutes in the future"
    )
    
    if success and data:
        pred = data['prediction']
        print(f"\nResults:")
        print(f"  Predicted Temperature: {pred['predicted_temperature']}°C")
        print(f"  Confidence: {pred['confidence_percentage']}%")
        print(f"  Minutes Ahead: {pred['minutes_ahead']}")
        print(f"  Trend Slope: {pred['model_slope']} °C/min")
        print(f"  Last Recorded: {pred['last_recorded_temp']}°C")
        print(f"  Data Points Used: {data['data_points_used']}")
        
        return True
    else:
        print_info("Prediction may require 10+ minutes of historical data")
        return False

def test_multiple_predictions():
    """Test /api/predict/multiple endpoint"""
    print_header("TEST 2: Multiple Predictions")
    
    success, data = test_endpoint(
        "Multiple Predictions",
        "/api/predict/multiple",
        params={'intervals': '15,30,60,120'},
        description="Predictions at 15, 30, 60, and 120 minutes ahead"
    )
    
    if success and data:
        preds = data['predictions_data']['predictions']
        print(f"\nResults:")
        print(f"  Number of Predictions: {len(preds)}")
        print(f"  Trend Direction: {data['predictions_data']['trend_direction']}")
        print(f"  Data Points Used: {data['data_points_used']}\n")
        
        for pred in preds:
            print(f"  +{pred['minutes_ahead']}min: {pred['predicted_temperature']}°C ({pred['confidence_percentage']}%)")
        
        return True
    else:
        print_info("Multiple predictions require historical data")
        return False

def test_24h_forecast():
    """Test /api/predict/24h-forecast endpoint"""
    print_header("TEST 3: 24-Hour Forecast")
    
    success, data = test_endpoint(
        "24-Hour Forecast",
        "/api/predict/24h-forecast",
        description="Hourly temperature predictions for next 24 hours"
    )
    
    if success and data:
        forecast = data['forecast_24h']
        summary = forecast['summary']
        hourly = forecast['hourly_forecast']
        
        print(f"\nResults:")
        print(f"  Hours Forecasted: {len(hourly)}")
        print(f"  Data Points Used: {data['data_points_used']}\n")
        
        print(f"  Summary Statistics:")
        print(f"    Max Temperature: {summary['predicted_max']}°C (Hour {summary['max_hour']})")
        print(f"    Min Temperature: {summary['predicted_min']}°C (Hour {summary['min_hour']})")
        print(f"    Avg Temperature: {summary['predicted_avg']}°C")
        print(f"    Trend (24h): {forecast['trend_24h']}\n")
        
        print(f"  First 6 hours:")
        for h in hourly[:6]:
            print(f"    Hour {h['hour']:2d}: {h['predicted_temperature']}°C ({h['confidence_percentage']}%)")
        
        return True
    else:
        print_info("24h forecast requires historical data")
        return False

def test_moving_average():
    """Test /api/predict/moving-average endpoint"""
    print_header("TEST 4: Moving Average (Smoothed Data)")
    
    success, data = test_endpoint(
        "Moving Average",
        "/api/predict/moving-average",
        params={'window': 5},
        description="Temperature data smoothed with moving average (window=5)"
    )
    
    if success and data:
        ma_data = data['moving_average']
        print(f"\nResults:")
        print(f"  Total Data Points: {len(ma_data)}")
        print(f"  Window Size: {data['window_size']}\n")
        
        if len(ma_data) > 0:
            print(f"  Last 5 readings (smoothed):")
            for point in ma_data[-5:]:
                print(f"    {point['timestamp']}: {point['temperature']}°C")
        
        return True
    else:
        print_info("Moving average requires historical data")
        return False

def test_anomaly_detection():
    """Test /api/predict/anomalies endpoint"""
    print_header("TEST 5: Anomaly Detection")
    
    success, data = test_endpoint(
        "Anomaly Detection",
        "/api/predict/anomalies",
        params={'threshold_std': 2.0},
        description="Detects unusual temperature readings (sensor health check)"
    )
    
    if success and data:
        analysis = data['anomaly_analysis']
        
        print(f"\nResults:")
        print(f"  Mean Temperature: {analysis['mean_temperature']}°C")
        print(f"  Std Deviation: {analysis['std_deviation']}°C")
        print(f"  Anomaly Threshold: ±{analysis['anomaly_threshold']}°C")
        print(f"  Anomalies Detected: {analysis['anomalies_detected']}\n")
        
        if analysis['anomalies']:
            print(f"  Top Anomalies (up to 3):")
            for anom in analysis['anomalies'][:3]:
                print(f"    {anom['timestamp']}: {anom['temperature']}°C ({anom['std_devs_away']}σ away)")
                print(f"      Deviation: ±{anom['deviation']}°C")
        else:
            print_success("No anomalies detected - data quality is good!")
        
        return True
    else:
        print_info("Anomaly detection requires historical data")
        return False

def test_existing_endpoints():
    """Test that existing endpoints still work"""
    print_header("TEST 6: Existing Endpoints (Regression Test)")
    
    endpoints = [
        ('/api/latest', 'Latest Reading'),
        ('/api/history', 'Historical Data'),
        ('/api/alert-status', 'Alert Status'),
        ('/api/alert-history', 'Alert History'),
    ]
    
    all_passed = True
    for endpoint, name in endpoints:
        success, _ = test_endpoint(f"Existing: {name}", endpoint)
        if not success:
            all_passed = False
    
    return all_passed

def print_summary(results):
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    test_names = [
        "Single Prediction",
        "Multiple Predictions",
        "24-Hour Forecast",
        "Moving Average",
        "Anomaly Detection",
        "Existing Endpoints"
    ]
    
    passed = sum(1 for r in results if r)
    total = len(results)
    
    print(f"{Colors.BOLD}Results:{Colors.ENDC}\n")
    
    for name, result in zip(test_names, results):
        status = f"{Colors.GREEN}✅ PASS{Colors.ENDC}" if result else f"{Colors.YELLOW}⚠️  WARN{Colors.ENDC}"
        print(f"  {name:.<40} {status}")
    
    print(f"\n{Colors.BOLD}Total:{Colors.ENDC} {passed}/{total} tests passed\n")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 All Tests Passed!{Colors.ENDC}\n")
    elif passed >= total - 1:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  Some Tests Skipped (need historical data){Colors.ENDC}\n")
        print_info("Wait 10+ minutes for the system to collect data, then run this script again")
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ Some Tests Failed{Colors.ENDC}\n")
        print_info("Check the errors above")

def main():
    """Main test flow"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║     🔮 TEMPERATURE PREDICTION - TEST SUITE                     ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Starting tests at {datetime.now().strftime('%H:%M:%S')}{Colors.ENDC}\n")
    
    # Check server
    if not check_server():
        return False
    
    # Run tests
    results = [
        test_single_prediction(),
        test_multiple_predictions(),
        test_24h_forecast(),
        test_moving_average(),
        test_anomaly_detection(),
        test_existing_endpoints(),
    ]
    
    # Print summary
    print_summary(results)
    
    print(f"{Colors.BOLD}Test Completed at {datetime.now().strftime('%H:%M:%S')}{Colors.ENDC}\n")
    
    return all(results)

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
