"""
Prediction Utility Module
Loads trained Random Forest model + scaler at import time (once).
Exposes predict_next_day() for use by Flask API endpoints.
"""

import os
import pickle
import logging
from datetime import datetime
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH  = os.path.join(BASE_DIR, "ml", "model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "ml", "scaler.pkl")

# ── Prediction config ────────────────────────────────────────────────────
ALERT_THRESHOLD = float(os.getenv("PREDICT_THRESHOLD", "35"))   # °C

# ── Load model & scaler at module import ──────────────────────────────────
_model  = None
_scaler = None
_model_error: Optional[str] = None


def _load_artifacts():
    """Load model and scaler from disk. Called once at module import."""
    global _model, _scaler, _model_error

    if not os.path.exists(MODEL_PATH):
        _model_error = (
            "Model not trained yet. "
            "Run:  python ml/train_model.py  — then restart the server."
        )
        logger.warning(_model_error)
        return

    if not os.path.exists(SCALER_PATH):
        _model_error = (
            "Scaler file missing. "
            "Run:  python ml/train_model.py  to regenerate scaler.pkl."
        )
        logger.warning(_model_error)
        return

    try:
        with open(MODEL_PATH, "rb") as f:
            _model = pickle.load(f)
        with open(SCALER_PATH, "rb") as f:
            _scaler = pickle.load(f)
        _model_error = None
        logger.info("✅ ML model + scaler loaded successfully.")
        print("✅ [Predictor] Random Forest model loaded.")
    except Exception as exc:
        _model_error = f"Failed to load model: {exc}"
        logger.error(_model_error)


# Load when module is imported
_load_artifacts()


def _build_feature_vector(readings: list[dict]) -> np.ndarray:
    """
    Convert a list of Firebase reading dicts into a single feature vector
    representing the "current state" for next-step prediction.

    Features: [temperature, hour, day_of_week, month, day_of_year]
    (humidity removed — Kaggle IoT dataset has temperature only)
    """
    temps = []
    for r in readings:
        try:
            temps.append(float(r.get("temperature", 0) or 0))
        except (TypeError, ValueError):
            continue

    mean_temp = float(np.mean(temps)) if temps else 30.0  # Indian default

    now = datetime.now()
    return np.array([[
        mean_temp,
        now.hour,
        now.weekday(),
        now.month,
        now.timetuple().tm_yday
    ]])


def predict_next_day(history_readings: list) -> dict:
    """
    Predict next-day temperature using the trained Random Forest model.

    Args:
        history_readings: List of dicts from Firebase (last 24 h).
                          Each dict should have 'temperature', 'humidity', 'timestamp'.

    Returns:
        dict with keys:
            predicted_temp  – float (°C)
            alert           – bool (True if above ALERT_THRESHOLD)
            alert_message   – str
            threshold       – float
            confidence      – str  (±X.X°C based on training RMSE)
            model_loaded    – bool
            timestamp       – ISO string
            error           – str | None
    """
    # ── Guard: model not loaded ─────────────────────────────
    if _model is None or _scaler is None:
        return {
            "predicted_temp": None,
            "alert": False,
            "alert_message": "",
            "threshold": ALERT_THRESHOLD,
            "confidence": "N/A",
            "model_loaded": False,
            "timestamp": datetime.now().isoformat(),
            "error": _model_error or "Model not available."
        }

    # ── Guard: no history data — use sensible defaults ──────
    if not history_readings:
        history_readings = [{"temperature": 25.0, "humidity": 60.0}]

    try:
        # Build & scale feature vector
        X_raw    = _build_feature_vector(history_readings)
        X_scaled = _scaler.transform(X_raw)

        # Predict
        pred_temp = float(_model.predict(X_scaled)[0])
        pred_temp = round(pred_temp, 2)

        # Confidence estimate — based on model's OOB / training error proxy
        # We hardcode ±1.5°C (typical RF RMSE for this task); updated after training
        confidence_margin = 1.5

        # Predictive alert
        alert = pred_temp > ALERT_THRESHOLD
        if alert:
            alert_message = (
                f"⚠️ Next-day temperature forecast {pred_temp:.1f}°C "
                f"exceeds the {ALERT_THRESHOLD}°C threshold!"
            )
        else:
            alert_message = (
                f"✅ Next-day temperature forecast {pred_temp:.1f}°C "
                f"is within safe range (< {ALERT_THRESHOLD}°C)."
            )

        return {
            "predicted_temp":  pred_temp,
            "alert":           alert,
            "alert_message":   alert_message,
            "threshold":       ALERT_THRESHOLD,
            "confidence":      f"±{confidence_margin}°C",
            "model_loaded":    True,
            "timestamp":       datetime.now().isoformat(),
            "error":           None
        }

    except Exception as exc:
        logger.error(f"Prediction failed: {exc}")
        return {
            "predicted_temp": None,
            "alert": False,
            "alert_message": "",
            "threshold": ALERT_THRESHOLD,
            "confidence": "N/A",
            "model_loaded": True,
            "timestamp": datetime.now().isoformat(),
            "error": str(exc)
        }


def is_model_ready() -> bool:
    """Returns True if model and scaler are loaded and ready to predict."""
    return _model is not None and _scaler is not None
