"""
Test Email Alert System
Run this script to verify your email configuration is working correctly.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.email_config import email_alert_service, TEMPERATURE_THRESHOLD
from utils.alert_monitor import TemperatureAlertMonitor
from datetime import datetime


def print_banner(text):
    """Print formatted banner"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")


def test_email_credentials():
    """Step 1: Validate email credentials"""
    print_banner("STEP 1: Validating Email Credentials")
    
    if not email_alert_service.validate_credentials():
        print("❌ EMAIL CREDENTIALS NOT CONFIGURED")
        print("\n   Please follow these steps:")
        print("   1. Open .env file in this project directory")
        print("   2. Set EMAIL_USER and EMAIL_PASS")
        print("   3. Re-run this test\n")
        return False
    
    print(f"✅ EMAIL_USER : {email_alert_service.sender_email}")
    print(f"✅ EMAIL_PASS : {'*' * 10} (hidden for security)\n")
    return True


def test_email_send():
    """Step 2: Send test email"""
    print_banner("STEP 2: Sending Test Email")
    
    test_temp = 55.5
    test_humidity = 75.0
    timestamp = datetime.now().isoformat()
    
    print(f"📧 Preparing test email...")
    print(f"   Temperature: {test_temp}°C")
    print(f"   Humidity: {test_humidity}%")
    print(f"   Threshold: {TEMPERATURE_THRESHOLD}°C\n")
    
    subject, body = email_alert_service.create_alert_email(
        temperature=test_temp,
        humidity=test_humidity,
        timestamp=timestamp,
        device_name="TEST-SENSOR"
    )
    
    print(f"📧 Sending test email to {email_alert_service.sender_email}...\n")
    
    if email_alert_service.send_email(subject, body):
        print("\n✅ TEST EMAIL SENT SUCCESSFULLY!\n")
        return True
    else:
        print("\n❌ FAILED TO SEND TEST EMAIL\n")
        print("   Troubleshooting tips:")
        print("   1. Verify EMAIL_USER is correct")
        print("   2. Generate App Password at: https://myaccount.google.com/apppasswords")
        print("   3. Make sure 2-Factor Authentication is enabled")
        print("   4. Check internet connection\n")
        return False


def test_alert_logic():
    """Step 3: Test alert triggering logic"""
    print_banner("STEP 3: Testing Alert Logic (Simulation)")
    
    print("Testing alert state transitions...\n")
    
    # Scenario 1: Normal temperature
    print("📊 Scenario 1: Temperature NORMAL (35°C)")
    result1 = TemperatureAlertMonitor.check_temperature(
        temperature=35.0,
        humidity=50.0,
        timestamp=datetime.now().isoformat(),
        device_name="SIM-SENSOR"
    )
    print(f"   Result: {result1['message']}")
    print(f"   Alert Sent: {result1['alert_sent']}\n")
    
    # Scenario 2: Temperature exceeds threshold
    print(f"📊 Scenario 2: Temperature EXCEEDED ({TEMPERATURE_THRESHOLD + 5}°C)")
    result2 = TemperatureAlertMonitor.check_temperature(
        temperature=TEMPERATURE_THRESHOLD + 5,
        humidity=60.0,
        timestamp=datetime.now().isoformat(),
        device_name="SIM-SENSOR"
    )
    print(f"   Result: {result2['message']}")
    print(f"   Alert Sent: {result2['alert_sent']}\n")
    
    # Scenario 3: Second alert should be suppressed (cooldown)
    print("📊 Scenario 3: Temperature still HIGH (immediate retry)")
    result3 = TemperatureAlertMonitor.check_temperature(
        temperature=TEMPERATURE_THRESHOLD + 3,
        humidity=62.0,
        timestamp=datetime.now().isoformat(),
        device_name="SIM-SENSOR"
    )
    print(f"   Result: {result3['message']}")
    print(f"   Alert Sent: {result3['alert_sent']} (should be False - in cooldown)\n")
    
    # Scenario 4: Temperature returns to normal
    print("📊 Scenario 4: Temperature NORMALIZED (40°C)")
    result4 = TemperatureAlertMonitor.check_temperature(
        temperature=40.0,
        humidity=55.0,
        timestamp=datetime.now().isoformat(),
        device_name="SIM-SENSOR"
    )
    print(f"   Result: {result4['message']}\n")
    
    TemperatureAlertMonitor.reset_alerts()  # Reset for next test
    print("✅ ALERT LOGIC TEST COMPLETED\n")
    return True


def test_alert_status():
    """Step 4: Check alert system status"""
    print_banner("STEP 4: Alert System Status")
    
    status = TemperatureAlertMonitor.get_alert_status()
    
    print(f"🔴 Alert Active: {status['alert_active']}")
    print(f"🔔 Threshold: {status['threshold']}°C")
    print(f"⏱️  Cooldown: {status['cooldown_seconds']}s ({status['cooldown_seconds']//60}m)")
    print(f"🌡️  Last Temp: {status['last_temperature']}")
    print(f"📊 Recent Alerts: {len(status['recent_alerts'])}\n")
    
    return True


def main():
    """Run all tests"""
    print("\n")
    print(" " * 70)
    print("  🌡️  TEMPERATURE MONITORING SYSTEM - EMAIL ALERT TEST")
    print(" " * 70)
    
    tests = [
        ("Email Credentials", test_email_credentials),
        ("Email Send", test_email_send),
        ("Alert Logic", test_alert_logic),
        ("Alert Status", test_alert_status),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ ERROR in {test_name}: {e}\n")
            failed += 1
    
    # Summary
    print_banner("TEST SUMMARY")
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Your email alert system is ready to use.\n")
    else:
        print(f"\n⚠️  Some tests failed. Please fix the issues above.\n")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
