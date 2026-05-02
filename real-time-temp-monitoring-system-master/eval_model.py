"""
Deep Model Accuracy Evaluation
Loads the trained Random Forest model and evaluates it on the test set
with full metrics: MAE, RMSE, R2, MAPE, and prediction error distribution.
"""

import sys
import os
import pickle
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml.preprocess import load_and_prepare

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH  = os.path.join(BASE_DIR, "ml", "model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "ml", "scaler.pkl")

print("=" * 60)
print("  AI / ML MODEL ACCURACY EVALUATION")
print("  Random Forest Regressor — Temperature Predictor")
print("=" * 60)

# ── Load model ────────────────────────────────────────────────
print("\n[1] Loading model...")
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)
print(f"    Model type      : {type(model).__name__}")
print(f"    n_estimators    : {model.n_estimators}")
print(f"    max_depth       : {model.max_depth}")

# ── Load test data ────────────────────────────────────────────
print("\n[2] Loading & preprocessing dataset...")
X_train, X_test, y_train, y_test, scaler = load_and_prepare()
print(f"    Training samples: {len(X_train):,}")
print(f"    Test samples    : {len(X_test):,}")
print(f"    Temp range (test): {y_test.min():.1f}°C — {y_test.max():.1f}°C")

# ── Predictions ───────────────────────────────────────────────
print("\n[3] Running predictions on test set...")
y_pred = model.predict(X_test)

# ── Core metrics ──────────────────────────────────────────────
errors     = np.abs(y_test - y_pred)
mae        = np.mean(errors)
rmse       = np.sqrt(np.mean((y_test - y_pred) ** 2))
ss_res     = np.sum((y_test - y_pred) ** 2)
ss_tot     = np.sum((y_test - np.mean(y_test)) ** 2)
r2         = 1 - (ss_res / ss_tot)
mape       = np.mean(np.abs((y_test - y_pred) / np.clip(np.abs(y_test), 0.1, None))) * 100
max_err    = np.max(errors)
median_err = np.median(errors)

# Accuracy within tolerance bands
within_1   = np.mean(errors <= 1.0) * 100
within_2   = np.mean(errors <= 2.0) * 100
within_5   = np.mean(errors <= 5.0) * 100

print("\n" + "=" * 60)
print("  ACCURACY METRICS")
print("=" * 60)
print(f"\n  MAE   (Mean Absolute Error)       : {mae:.3f} °C")
print(f"  RMSE  (Root Mean Squared Error)   : {rmse:.3f} °C")
print(f"  R²    (R-squared / fit quality)   : {r2:.4f}  ({r2*100:.1f}%)")
print(f"  MAPE  (Mean Abs % Error)          : {mape:.2f}%")
print(f"  Median Error                      : {median_err:.3f} °C")
print(f"  Max Error (worst case)            : {max_err:.3f} °C")

print("\n  TOLERANCE BANDS (how often prediction is within N°C of real):")
bar1 = "#" * int(within_1 / 2)
bar2 = "#" * int(within_2 / 2)
bar5 = "#" * int(within_5 / 2)
print(f"  Within ±1°C  : {bar1:<50} {within_1:.1f}%")
print(f"  Within ±2°C  : {bar2:<50} {within_2:.1f}%")
print(f"  Within ±5°C  : {bar5:<50} {within_5:.1f}%")

# ── Feature importances ───────────────────────────────────────
print("\n  FEATURE IMPORTANCES (what the model relies on):")
feature_names = ["temperature", "hour", "day_of_week", "month", "day_of_year"]
importances   = model.feature_importances_
for fname, imp in sorted(zip(feature_names, importances), key=lambda x: -x[1]):
    bar = "#" * int(imp * 50)
    print(f"  {fname:<15} {bar:<50} {imp*100:.1f}%")

# ── R² interpretation ─────────────────────────────────────────
print("\n  R² INTERPRETATION:")
if r2 >= 0.95:
    grade = "EXCELLENT — near-perfect fit"
elif r2 >= 0.85:
    grade = "VERY GOOD — strong predictive power"
elif r2 >= 0.70:
    grade = "GOOD — solid model"
elif r2 >= 0.50:
    grade = "MODERATE — useful but improvable"
else:
    grade = "POOR — needs retraining"
print(f"  R² = {r2:.4f}  =>  {grade}")

# ── Sample predictions ────────────────────────────────────────
print("\n  SAMPLE PREDICTIONS (first 10 from test set):")
print(f"  {'#':<4}  {'Actual':>8}  {'Predicted':>10}  {'Error':>8}  {'Status':>10}")
print("  " + "-" * 48)
for i in range(min(10, len(y_test))):
    actual = y_test[i]
    pred   = y_pred[i]
    err    = abs(actual - pred)
    status = "GOOD" if err <= 2.0 else ("OK" if err <= 5.0 else "HIGH")
    print(f"  {i+1:<4}  {actual:>7.2f}°C  {pred:>9.2f}°C  {err:>7.2f}°C  {status:>10}")

print("\n" + "=" * 60)
print("  SUMMARY")
print("=" * 60)
print(f"""
  Model      : Random Forest Regressor (150 trees, depth 12)
  Training   : {len(X_train):,} samples  |  Test: {len(X_test):,} samples
  MAE        : {mae:.2f}°C  (avg prediction error)
  RMSE       : {rmse:.2f}°C  (penalises big errors more)
  R²         : {r2:.4f}  ({r2*100:.1f}% variance explained)
  ±1°C band  : {within_1:.1f}% of predictions
  ±2°C band  : {within_2:.1f}% of predictions
  Grade      : {grade}
""")
