@echo off
REM ─────────────────────────────────────────────────────────────
REM  ML Prediction System — One-Time Training Launcher
REM  Run this once before starting app.py
REM ─────────────────────────────────────────────────────────────

echo.
echo ============================================================
echo   ESP32 IoT  ^|  ML Prediction Setup
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/2] Generating climate dataset (17,520 rows)...
python data/generate_dataset.py
if errorlevel 1 (
    echo ERROR: Dataset generation failed.
    pause
    exit /b 1
)

echo.
echo [2/2] Training Random Forest model...
python -X utf8 ml/train_model.py
if errorlevel 1 (
    echo ERROR: Model training failed.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Training complete! model.pkl and scaler.pkl are ready.
echo   You can now run:  python app.py
echo ============================================================
echo.
pause
