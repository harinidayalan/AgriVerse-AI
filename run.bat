@echo off
title AgriVerse AI - Intelligent Smart Farming Ecosystem
echo ========================================================
echo   AgriVerse AI - Intelligent Smart Farming Ecosystem
echo   Unified Single Link: http://localhost:5000
echo ========================================================
echo Opening AgriVerse AI in your default browser...
start http://localhost:5000
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe app.py
) else (
    python app.py
)
pause
