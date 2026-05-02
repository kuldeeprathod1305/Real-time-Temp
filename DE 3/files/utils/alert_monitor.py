"""
Temperature Alert Monitor
Monitors temperature readings and triggers alerts when thresholds are exceeded.
"""

from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta

# Indian Standard Time (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))


class TemperatureAlertMonitor:
    """
    Monitors temperature readings and manages alert triggers.
    Provides class-level methods for alert management.
    """
    
    high_threshold = 35.0
    low_threshold = 15.0
    alert_history = []
    last_alert_sent = {}
    
    @classmethod
    def check_temperature(cls, temperature: float, humidity: float = None, 
                         timestamp: str = None, device_name: str = "Unknown") -> Dict:
        """
        Check temperature against thresholds and generate alert if needed.
        
        Args:
            temperature: Current temperature reading
            humidity: Humidity reading (optional)
            timestamp: Timestamp of reading (optional)
            device_name: Name of the device (optional)
            
        Returns:
            Alert dictionary with status and message
        """
        alert_triggered = False
        alert_reason = None
        alert_sent = False
        
        if temperature > cls.high_threshold:
            alert_triggered = True
            alert_reason = f"HIGH_TEMPERATURE ({temperature}°C > {cls.high_threshold}°C)"
        
        elif temperature < cls.low_threshold:
            alert_triggered = True
            alert_reason = f"LOW_TEMPERATURE ({temperature}°C < {cls.low_threshold}°C)"
        
        if alert_triggered:
            alert = {
                "type": alert_reason.split('_')[0] + "_" + alert_reason.split('_')[1] if '_' in alert_reason else alert_reason,
                "temperature": temperature,
                "humidity": humidity,
                "timestamp": timestamp or datetime.now(IST).isoformat(),
                "device_name": device_name,
                "reason": alert_reason,
                "message": f"⚠️ {alert_reason} at {device_name}"
            }
            cls.alert_history.append(alert)
            alert_sent = True
        
        return {
            "alert_triggered": alert_triggered,
            "alert_reason": alert_reason,
            "alert_sent": alert_sent,
            "message": f"✅ Temp check OK" if not alert_triggered else f"⚠️ Alert triggered: {alert_reason}",
            "temperature": temperature,
            "humidity": humidity
        }
    
    @classmethod
    def get_alert_status(cls) -> Dict:
        """Get current alert system status."""
        return {
            "status": "active",
            "high_threshold": cls.high_threshold,
            "low_threshold": cls.low_threshold,
            "total_alerts": len(cls.alert_history),
            "recent_alerts": cls.alert_history[-5:] if cls.alert_history else []
        }
    
    @classmethod
    def get_recent_alerts(cls, hours: int = 24) -> List[Dict]:
        """
        Get alerts from the last N hours.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of recent alerts
        """
        cutoff_time = datetime.now(IST) - timedelta(hours=hours)
        return [
            alert for alert in cls.alert_history
            if datetime.fromisoformat(alert.get("timestamp", datetime.now(IST).isoformat())) >= cutoff_time
        ]
    
    @classmethod
    def reset_alerts(cls):
        """Reset alert state."""
        cls.alert_history = []
        cls.last_alert_sent = {}
    
    @classmethod
    def clear_history(cls):
        """Clear alert history."""
        cls.alert_history = []


def get_alert_history(hours: int = 24) -> List[Dict]:
    """
    Get alert history for the last N hours.
    
    Args:
        hours: Number of hours to look back
        
    Returns:
        List of alerts
    """
    return TemperatureAlertMonitor.get_recent_alerts(hours)
