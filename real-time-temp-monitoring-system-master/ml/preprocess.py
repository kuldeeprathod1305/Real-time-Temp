"""
Data Preprocessing Pipeline
Loads the climate CSV dataset, engineers time-based features,
normalizes data, and prepares train/test splits for ML model training.
"""

import os
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

# ── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH   = os.path.join(BASE_DIR, "data", "iot_temp_india.csv")    # Indian IoT dataset
SCALER_PATH = os.path.join(BASE_DIR, "ml", "scaler.pkl")

# Feature columns used by the model (temperature only — no humidity in IoT dataset)
FEATURE_COLS = ["temperature", "hour", "day_of_week", "month", "day_of_year"]
TARGET_COL   = "next_temperature"


def load_and_prepare(data_path: str = DATA_PATH, test_size: float = 0.2):
    """
    Loads CSV, cleans data, creates time features,
    normalizes, and returns train/test splits.

    Returns:
        X_train, X_test, y_train, y_test, scaler
    """
    print("=" * 55)
    print("  ML Preprocessing Pipeline")
    print("=" * 55)

    # ── 1. Load ─────────────────────────────────────────────
    print(f"📂 Loading dataset from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"   ✅ Loaded {len(df):,} rows × {len(df.columns)} columns")
    print(f"   Columns: {list(df.columns)}")

    # ── 2. Normalise column names ────────────────────────────
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # ── Kaggle IoT dataset exact column names ───────────────────────────────
    # Raw columns: 'id', 'room_id/id', 'noted_date', 'temp', 'out/in'
    # Rename them explicitly if present, else fall back to fuzzy matching
    explicit_map = {
        "noted_date": "datetime",
        "temp":       "temperature",
    }
    fuzzy_map = {}
    for c in df.columns:
        lc = c.lower()
        if c in explicit_map:
            fuzzy_map[c] = explicit_map[c]
        elif ("temp" in lc) and "temperature" not in fuzzy_map.values():
            fuzzy_map[c] = "temperature"
        elif any(x in lc for x in ["noted_date", "datetime", "date_time", "timestamp", "time", "date"]) \
             and "datetime" not in fuzzy_map.values():
            fuzzy_map[c] = "datetime"
    df.rename(columns=fuzzy_map, inplace=True)

    # Keep only indoor readings if 'out/in' column exists
    out_in_cols = [c for c in df.columns if "out" in c.lower() or c.lower() in ["out/in", "out_in"]]
    if out_in_cols:
        col = out_in_cols[0]
        before_filter = len(df)
        df = df[df[col].astype(str).str.strip().str.lower() == "in"]
        df.reset_index(drop=True, inplace=True)
        print(f"   🏠 Kept indoor readings only: {len(df):,} rows (from {before_filter:,})")

    required = {"temperature", "datetime"}
    missing  = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing required columns: {missing}\n"
                         f"Found: {list(df.columns)}")

    # ── 3. Parse datetime ────────────────────────────────────
    print("🕐 Parsing timestamps …")
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    before = len(df)
    df.dropna(subset=["datetime"], inplace=True)
    print(f"   Dropped {before - len(df):,} rows with unparseable timestamps")

    df.sort_values("datetime", inplace=True)
    df.reset_index(drop=True, inplace=True)

    # ── 4. Clean numeric columns ─────────────────────────────
    print("Cleaning numeric values ...")
    df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")

    # Valid Indian indoor temperature range: 0-60 degC
    df = df[(df["temperature"] >= 0) & (df["temperature"] <= 60)]
    df.dropna(subset=["temperature"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    print(f"   [OK] {len(df):,} clean rows remain")

    # ── 5. Time features ─────────────────────────────────────
    print("⚙️  Engineering time features …")
    df["hour"]        = df["datetime"].dt.hour
    df["day_of_week"] = df["datetime"].dt.dayofweek   # 0 = Monday
    df["month"]       = df["datetime"].dt.month
    df["day_of_year"] = df["datetime"].dt.dayofyear

    # ── 6. Target: next-step temperature ────────────────────
    df[TARGET_COL] = df["temperature"].shift(-1)
    df.dropna(subset=[TARGET_COL], inplace=True)
    df.reset_index(drop=True, inplace=True)
    print(f"   ✅ Target column '{TARGET_COL}' created")

    # ── 7. Build feature matrix ──────────────────────────────
    X = df[FEATURE_COLS].values
    y = df[TARGET_COL].values

    # ── 8. Normalize features ────────────────────────────────
    print("📏 Normalizing features with MinMaxScaler …")
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    # Persist scaler for inference
    os.makedirs(os.path.dirname(SCALER_PATH), exist_ok=True)
    with open(SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)
    print(f"   ✅ Scaler saved → {SCALER_PATH}")

    # ── 9. Train / test split ────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=test_size, shuffle=False   # time-series: no shuffle
    )
    print(f"   Train: {len(X_train):,} samples | Test: {len(X_test):,} samples")
    print("=" * 55)
    return X_train, X_test, y_train, y_test, scaler


if __name__ == "__main__":
    X_train, X_test, y_train, y_test, scaler = load_and_prepare()
    print("✅ Preprocessing complete.")
    print(f"   X_train shape : {X_train.shape}")
    print(f"   y_train range : {y_train.min():.1f} – {y_train.max():.1f} °C")
