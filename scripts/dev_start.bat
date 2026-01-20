@echo off
echo ============================================
echo   DEV MODE - Uruchamianie...
echo ============================================
echo.

echo [1/2] Uruchamiam backend (FastAPI)...
start "Backend - FastAPI" cmd /k "cd ..\backend && python main.py"

timeout /t 3 >nul

echo [2/2] Uruchamiam frontend (React)...
start "Frontend - React" cmd /k "cd ..\frontend && npm start"

echo.
echo ============================================
echo   DEV MODE uruchomiony!
echo ============================================
echo.
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://localhost:3000
echo.
echo React otworzy sie automatycznie w przegladarce
echo.
echo Aby zakonczyc:
echo - Zamknij oba okna terminala
echo - Lub nacisnij Ctrl+C w kazdym z nich
echo.
pause