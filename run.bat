@echo off
echo ===================================================
echo  ProjectPulse - Field Update & Schedule-Linking System
echo  SIH 2026 PS26122 - Oil India Limited
echo ===================================================
echo.
echo Installing/verifying dependencies...
python -m pip install -r requirements.txt
echo.
echo Launching dashboard...
streamlit run app.py
pause
