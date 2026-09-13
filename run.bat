@echo off
echo ===================================================
echo  Oil India Limited - Intelligent Schedule Linking Layer
echo  SIH PS26122 Infrastructure AI Solution
echo ===================================================
echo.
echo Installing/verifying dependencies...
python -m pip install -r requirements.txt
echo.
echo Launching Streamlit Dashboard...
streamlit run app.py
pause
