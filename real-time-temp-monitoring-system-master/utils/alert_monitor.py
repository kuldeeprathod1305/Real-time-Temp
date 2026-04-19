"""
Temperature Alert Monitor
Tracks temperature readings and triggers alerts when thresholds are exceeded.
Implements debounce/rate-limiting to prevent alert spam.
"""

import time
from datetime import datetime
from typing import Optional, Dict
from utils.email_config import email_alert_service, TEMPERATURE_THRESHOLD, ALERT_COOLDOWN_SECONDS

# Track alert states to prevent spam
alert_states = {
    "last_alert_time": 0,
    "alert_triggered": False,
    "last_temp": None,
    "alert_log": []
}

# Max alerts to store in memory (for dashboard display)
MAX_ALERT_LOG = 100


class TemperatureAlertMonitor:
    """
    Monitors temperature readings and manages alert triggering.
    Implements smart debouncing to avoid alert spam.
    """

    @staticmethod
    def check_temperature(temperature: float, humidity: float, 
                         timestamp: str, device_name: str = "ESP32") -> Dict[str, any]:
        """
        Checks if temperature exceeds threshold and sends alert if needed.
        
        Args:
            temperature: Temperature reading in °C
            humidity: Humidity reading in %
            timestamp: ISO format timestamp of reading
            device_name: Name of the device
            
        Returns:
            Dictionary with alert status and details
        """
        result = {
            "alert_sent": False,
            "alert_reason": None,
            "temperature_safe": temperature <= TEMPERATURE_THRESHOLD,
            "time_since_last_alert": None,
            "message": ""
        }

        current_time = time.time()
        time_since_last = current_time - alert_states["last_alert_time"]
        result["time_since_last_alert"] = time_since_last

        # Update last recorded temperature
        alert_states["last_temp"] = temperature

        # ==========================================
        # Case 1: Temperature exceeds threshold
        # ==========================================
        if temperature > TEMPERATURE_THRESHOLD:
            print(f"\n🔴 ALERT TRIGGERED: Temperature {temperature}°C exceeds threshold {TEMPERATURE_THRESHOLD}°C")

            # Check cooldown to prevent spam
            if alert_states["alert_triggered"]:
                if time_since_last < ALERT_COOLDOWN_SECONDS:
                    remaining = ALERT_COOLDOWN_SECONDS - time_since_last
                    print(f"   ⏳ Alert in cooldown. Next alert in {remaining:.0f}s")
                    result["message"] = f"Alert suppressed (in cooldown for {remaining:.0f}s)"
                    return result
                else:
                    print(f"   ✓ Cooldown expired. Sending alert.")
            
            # Send alert
            subject, body = email_alert_service.create_alert_email(
                temperature, humidity, timestamp, device_name
            )
            
            if email_alert_service.send_email(subject, body):
                result["alert_sent"] = True
                result["alert_reason"] = "TEMP_THRESHOLD_EXCEEDED"
                alert_states["alert_triggered"] = True
                alert_states["last_alert_time"] = current_time
                result["message"] = f"✅ Alert sent for temperatureexceeding {TEMPERATURE_THRESHOLD}°C"
                
                # Log alert
                _log_alert(temperature, humidity, timestamp, "THRESHOLD_EXCEEDED")
            else:
                result["message"] = "❌ Alert triggered but failed to send email"

        # ==========================================
        # Case 2: Temperature returns to normal
        # ==========================================
        elif temperature <= TEMPERATURE_THRESHOLD and alert_states["alert_triggered"]:
            print(f"\n🟢 Temperature returned to normal: {temperature}°C")
            alert_states["alert_triggered"] = False
            result["message"] = f"✓ Temperature normal. Alert reset."
            result["alert_reason"] = "TEMP_NORMALIZED"

        # ==========================================
        # Case 3: Normal operation
        # ==========================================
        else:
            result["message"] = f"✓ Temperature normal: {temperature}°C"

        return result

    @staticmethod
    def get_alert_status() -> Dict:
        """
        Returns current alert system status.
        Useful for dashboard/monitoring.
        """
        return {
            "alert_active": alert_states["alert_triggered"],
            "last_alert_time": datetime.fromtimestamp(alert_states["last_alert_time"]).isoformat() 
                              if alert_states["last_alert_time"] else None,
            "last_temperature": alert_states["last_temp"],
            "threshold": TEMPERATURE_THRESHOLD,
            "cooldown_seconds": ALERT_COOLDOWN_SECONDS,
            "recent_alerts": alert_states["alert_log"][-10:]  # Last 10 alerts
        }

    @staticmethod
    def reset_alerts():
        """
        Manually reset alert state (for testing/admin).
        """
        alert_states["alert_triggered"] = False
        alert_states["last_alert_time"] = 0
        print("🔄 Alert state reset")


def _log_alert(temperature: float, humidity: float, timestamp: str, reason: str):
    """
    Logs alert details for audit trail and dashboard.
    
    Args:
        temperature: Temperature at time of alert
        humidity: Humidity at time of alert
        timestamp: Timestamp of reading
        reason: Reason for alert (e.g., "THRESHOLD_EXCEEDED")
    """
    alert_record = {
        "datetime": datetime.now().isoformat(),
        "temperature": temperature,
        "humidity": humidity,
        "reading_timestamp": timestamp,
        "reason": reason,
        "threshold": TEMPERATURE_THRESHOLD
    }
    
    alert_states["alert_log"].append(alert_record)
    
    # Keep log size manageable
    if len(alert_states["alert_log"]) > MAX_ALERT_LOG:
        alert_states["alert_log"] = alert_states["alert_log"][-MAX_ALERT_LOG:]


def get_alert_history():
    """
    Returns alert history for logging/dashboard.
    """
    return alert_states["alert_log"].copy()
