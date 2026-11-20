@echo off
echo ========================================================
echo Starting ShelfVision AI Backend (FastAPI + OpenCV + YOLO)
echo ========================================================
cd /d "%~dp0..\backend"
call .venv\Scripts\activate.bat
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause

