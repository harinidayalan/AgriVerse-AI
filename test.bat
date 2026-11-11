@echo off
echo Running AgriVerse AI Test Suite...
if exist "venv\Scripts\pytest.exe" (
    venv\Scripts\pytest.exe -v tests/test_app.py
) else (
    pytest -v tests/test_app.py
)
pause
