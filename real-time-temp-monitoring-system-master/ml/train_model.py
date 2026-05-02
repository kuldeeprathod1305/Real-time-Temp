"""
Model Training Script — Random Forest Regressor
Trains on the preprocessed climate dataset, evaluates performance,
and saves the model + scaler to disk for use by the Flask API.

Usage:
    python ml/train_model.py
"""

import os
import sys
import pickle
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml.preprocess import load_and_prepare

# ── Paths ─────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "model.pkl")


def train():
    print("\n" + "=" * 55)
    print("  [ML]  Random Forest Temperature Predictor -- Training")
    print("=" * 55 + "\n")

    # ── 1. Load data ──────────────────────────────────────────
    X_train, X_test, y_train, y_test, scaler = load_and_prepare()

    # ── 2. Build model ────────────────────────────────────────
    print("[*] Building Random Forest Regressor ...")
    model = RandomForestRegressor(
        n_estimators=150,
        max_depth=12,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features="sqrt",
        n_jobs=-1,           # use all CPU cores
        random_state=42
    )

    # ── 3. Train ──────────────────────────────────────────────
    print(f"[*] Training on {len(X_train):,} samples ...")
    model.fit(X_train, y_train)
    print("   [OK] Training complete!")

    # ── 4. Evaluate ───────────────────────────────────────────
    y_pred = model.predict(X_test)

    mae  = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    ss_res = np.sum((y_test - y_pred) ** 2)
    ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
    r2   = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0

    print("\n" + "-" * 40)
    print("  [Stats]  Evaluation Results (Test Set)")
    print("-" * 40)
    print(f"  MAE  (Mean Absolute Error)  : {mae:.3f} C")
    print(f"  RMSE (Root Mean Sq. Error)  : {rmse:.3f} C")
    print(f"  R2   (Coefficient of Det.)  : {r2:.4f}")
    print("-" * 40)

    # Feature importance
    feature_names = ["temperature", "hour", "day_of_week", "month", "day_of_year"]
    importances   = model.feature_importances_
    print("\n  [i]  Feature Importances:")
    for fname, imp in sorted(zip(feature_names, importances), key=lambda x: -x[1]):
        bar = "#" * int(imp * 40)
        print(f"    {fname:<15} {bar} {imp:.3f}")

    # ── 5. Save model ─────────────────────────────────────────
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    print(f"\n[OK] Model saved  -> {MODEL_PATH}")
    print("[OK] Ready to serve predictions via Flask /predict endpoint.\n")

    # ── 6. Quick sanity-check prediction ─────────────────────
    sample = X_test[:1]
    pred   = model.predict(sample)[0]
    actual = y_test[0]
    print(f"  [test] Sample prediction : {pred:.2f} C  (actual: {actual:.2f} C)")
    print("=" * 55 + "\n")

    return model, mae, rmse, r2


if __name__ == "__main__":
    train()
