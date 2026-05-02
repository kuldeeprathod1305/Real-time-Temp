"""
Indian IoT Temperature Dataset Generator
Generates realistic hourly indoor temperature readings based on
actual Indian seasonal and daily patterns.

Season profiles (indoor temps):
  Summer  (Mar-Jun): 28-44 degC  — dry heat
  Monsoon (Jul-Sep): 26-35 degC  — humid, cooler
  Autumn  (Oct-Nov): 22-32 degC  — pleasant
  Winter  (Dec-Feb): 12-24 degC  — cool nights
"""

import os
import numpy as np
import pandas as pd

# ── Output path ──────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(BASE_DIR, "iot_temp_india.csv")

# ── Reproducibility ───────────────────────────────────────────────────────────
np.random.seed(42)


def get_season_base(month):
    """Return (base_temp, amplitude, noise_std) for a given month."""
    if month in [3, 4, 5, 6]:      # Summer: March-June
        return 36.0, 6.0, 1.5
    elif month in [7, 8, 9]:       # Monsoon: July-September
        return 30.0, 4.0, 1.2
    elif month in [10, 11]:        # Post-monsoon: October-November
        return 26.0, 5.0, 1.0
    else:                           # Winter: December-February
        return 18.0, 6.0, 1.2


def generate_temp(dt):
    """
    Generate indoor temperature for a given datetime.
    Models: seasonal base + daily cycle (cooler at night) + random noise.
    """
    base, amp, noise_std = get_season_base(dt.month)

    # Daily cycle: peak around 14:00, trough around 02:00
    # +cos peaks at 0 angle (i.e. hour=14) -> correct afternoon peak
    hour_angle = (dt.hour - 14) * (2 * np.pi / 24)
    daily_effect = +amp * np.cos(hour_angle)

    noise = np.random.normal(0, noise_std)

    temp = base + daily_effect + noise
    return round(float(np.clip(temp, 10.0, 50.0)), 2)


def main():
    print("=" * 55)
    print("  Indian IoT Temperature Dataset Generator")
    print("=" * 55)

    # 2 years of hourly readings: Jan 2022 - Dec 2023
    start = pd.Timestamp("2022-01-01 00:00:00")
    end   = pd.Timestamp("2023-12-31 23:00:00")
    timestamps = pd.date_range(start=start, end=end, freq="h")

    print(f"  Generating {len(timestamps):,} hourly readings ...")

    records = []
    for ts in timestamps:
        records.append({
            "noted_date": ts.strftime("%m/%d/%Y %H:%M"),
            "temp":       generate_temp(ts),
            "out/in":     "In"
        })

    df = pd.DataFrame(records)

    # Stats
    print(f"\n  Temperature range : {df['temp'].min():.1f} degC - {df['temp'].max():.1f} degC")
    print(f"  Mean temperature  : {df['temp'].mean():.1f} degC")
    print(f"  Total rows        : {len(df):,}")

    monthly = df.copy()
    monthly["noted_date"] = pd.to_datetime(monthly["noted_date"])
    monthly["month"] = monthly["noted_date"].dt.strftime("%b")
    monthly["year"]  = monthly["noted_date"].dt.year
    print("\n  Monthly averages (2022):")
    m2022 = monthly[monthly["year"] == 2022].groupby(
        monthly[monthly["year"] == 2022]["noted_date"].dt.month
    )["temp"].mean()
    months = ["Jan","Feb","Mar","Apr","May","Jun",
              "Jul","Aug","Sep","Oct","Nov","Dec"]
    for i, avg in m2022.items():
        print(f"    {months[i-1]}: {avg:.1f} degC")

    # Save
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\n  [OK] Saved to: {OUTPUT_PATH}")
    print("=" * 55)


if __name__ == "__main__":
    main()
